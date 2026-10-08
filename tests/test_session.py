import json
from dataclasses import FrozenInstanceError
from types import SimpleNamespace as N
from unittest.mock import Mock
import pytest
from rve.session import ReflectionSession
from rve.reflection import BudgetExceeded, RuntimeLimits, generate_response


def response(content):
    return N(choices=[N(message=N(content=content), finish_reason='stop')],
             usage=N(prompt_tokens=10, completion_tokens=5))


def client(*answers):
    return N(chat=N(completions=N(create=Mock(side_effect=[response(a) for a in answers]))))


def interpretation(**changes):
    return json.dumps(dict(interpretation='You might need time to think.',
        alternatives=['The timing may simply be inconvenient.'], metaphor='',
        next_step='List your options.', question='What would you change?', source_ids=['r1']) | changes)


def test_rejection_correction_and_regeneration_preserve_history():
    s = ReflectionSession()
    original = s.report('I feel uncertain.')
    first, _ = s.interpret(client(interpretation(), '{"issues": []}'))
    feedback = s.feedback(first.id, 'reject', 'That does not fit.')
    corrected = s.report('I meant tired, not uncertain.', corrects=original.id)
    before = s.records
    c = client(interpretation(source_ids=[corrected.id]), '{"issues": []}')
    revised, _ = s.interpret(c)
    assert s.records[:len(before)] == before
    assert revised.refs == (corrected.id,)
    assert feedback.kind == 'human_feedback'
    context = c.chat.completions.create.call_args_list[0].kwargs['messages'][1]['content']
    assert 'That does not fit.' in context and 'I feel uncertain.' in context
    with pytest.raises(FrozenInstanceError):
        original.content = 'rewritten'
    assert json.loads(s.export())['schema_version'] == 1


@pytest.mark.parametrize('changes', [dict(source_ids=['missing']), dict(source_ids=['r2']),
    dict(metaphor='A spiral'), dict(alternatives=[]), dict(interpretation='')])
def test_invalid_interpretation_not_published(changes):
    s = ReflectionSession()
    s.report('A dilemma')
    with pytest.raises(ValueError):
        s.interpret(client(interpretation(**changes), '{"issues": []}'))
    assert not any(r.kind == 'interpretation' for r in s.records)
    assert json.loads(s.records[-1].content)['event'] == 'interpretation_rejected'


def test_symbolic_mode_and_direct_mode():
    for mode in ('symbolic', 'direct'):
        s = ReflectionSession()
        s.report('A dilemma')
        c = client(interpretation(metaphor='A crossroads' if mode == 'symbolic' else ''), '{"issues": []}')
        _, run = s.interpret(c, mode=mode)
        assert run.calls == (1 if mode == 'direct' else 2)


def test_incomplete_review_withholds_interpretation():
    s = ReflectionSession()
    s.report('A dilemma')
    with pytest.raises(ValueError, match='Review incomplete'):
        s.interpret(client(interpretation(), 'invalid'))
    assert [r.kind for r in s.records] == ['human_report', 'system_observation']


def test_output_budget_reserves_failed_or_unused_allowance():
    c = client('draft')
    run = generate_response(c, [{'role':'user', 'content':'x'}],
                            limits=RuntimeLimits(max_output_tokens=1200))
    assert run.calls == 1 and run.output_tokens_reserved == 1200
    assert run.status == 'critique_budget_exhausted_draft_retained'
    assert 'output_budget' in run.budget_events


def test_context_limit_prevents_dispatch():
    c = client('draft')
    with pytest.raises(BudgetExceeded):
        generate_response(c, [{'role':'user','content':'large'}], limits=RuntimeLimits(max_context_bytes=2))
    c.chat.completions.create.assert_not_called()


def test_late_response_discarded(monkeypatch):
    clock = iter([0, 0, 61])
    monkeypatch.setattr('rve.reflection.time.monotonic', lambda: next(clock))
    c = client('late')
    with pytest.raises(BudgetExceeded):
        generate_response(c, [{'role':'user','content':'x'}])
    assert c.chat.completions.create.call_args.kwargs['timeout'] == 60


def test_call_cap_and_retry_configuration():
    provider = client('draft')
    wrapper = N(with_options=Mock(return_value=provider))
    run = generate_response(wrapper, [{'role':'user','content':'x'}], limits=RuntimeLimits(max_calls=1))
    wrapper.with_options.assert_called_once_with(max_retries=0)
    assert run.calls == 1 and 'call_limit' in run.budget_events


@pytest.mark.parametrize('kwargs', [dict(max_calls=4), dict(max_output_tokens=0),
    dict(deadline_seconds=float('nan')), dict(max_context_bytes=-1)])
def test_invalid_limits(kwargs):
    with pytest.raises(ValueError):
        RuntimeLimits(**kwargs)


def test_pilot_packet_removes_condition_and_preserves_failures():
    from evaluation.meaning_pilot import packets, run_case, CASES
    row = run_case(client(interpretation(), '{"issues": []}', interpretation(), '{"issues": []}'),
                   CASES[0], 'plain', 'test')
    packet, key = packets([row])
    assert len(row['runs']) == 2
    assert 'condition' not in packet[0]
    assert all(r['kind'] != 'system_observation' for r in packet[0]['records'])
    assert all(v is None for v in packet[0]['scores'].values())
    failed = run_case(client('bad'), CASES[0], 'direct', 'test')
    assert failed['runs'][0]['status'] == 'failed'
    assert len(packets([failed])[0]) == 1
    assert key[0]['condition'] == 'plain'
