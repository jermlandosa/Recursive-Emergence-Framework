import json
from types import SimpleNamespace as N
from unittest.mock import Mock
import pytest
from rve.reflection import generate_response, parse_issues
from evaluation.ref_pilot import TASKS, score


def response(content, finish='stop', usage=True):
    return N(choices=[N(message=N(content=content), finish_reason=finish)],
             usage=N(prompt_tokens=10, completion_tokens=5) if usage else None)


def client_with(*responses):
    return N(chat=N(completions=N(create=Mock(side_effect=responses))))


def test_baseline_only_one_call():
    client = client_with(response('draft'))
    result = generate_response(client, [{'role': 'user', 'content': 'hello'}], reflection=False)
    assert result.answer == 'draft' and result.calls == 1 and result.status == 'baseline'


def test_clean_review_retains_draft():
    client = client_with(response('draft'), response('{"issues": []}'))
    result = generate_response(client, [{'role': 'user', 'content': 'hello'}])
    assert result.answer == 'draft' and result.calls == 2
    assert result.status == 'reviewed_unchanged' and result.prompt_tokens == 20


def test_revision_bounded_and_settings_fixed():
    issues = [{'kind': 'factual', 'detail': 'wrong sum', 'suggestion': 'recalculate'}]
    client = client_with(response('wrong'), response(json.dumps({'issues': issues})), response('correct'))
    context = [{'role': 'user', 'content': 'add'}]
    result = generate_response(client, context, model='fixed', temperature=0)
    assert result.answer == 'correct' and result.draft == 'wrong' and result.calls == 3
    assert result.completion_tokens == 15 and result.status == 'revised'
    for call in client.chat.completions.create.call_args_list:
        assert call.kwargs['model'] == 'fixed' and call.kwargs['temperature'] == 0
    assert context == [{'role': 'user', 'content': 'add'}]


@pytest.mark.parametrize('bad', ['not json', '{}', '{"issues": ["bad"]}'])
def test_invalid_review_retains_draft(bad):
    result = generate_response(client_with(response('draft'), response(bad)), [{'role': 'user', 'content': 'x'}])
    assert result.answer == 'draft' and result.status == 'critique_failed_draft_retained'


def test_provider_failure_during_review():
    result = generate_response(client_with(response('draft'), TimeoutError()), [{'role': 'user', 'content': 'x'}])
    assert result.answer == 'draft' and not result.usage_complete


def test_failed_revision_retains_draft():
    review = '{"issues": [{"kind":"unsupported","detail":"no evidence","suggestion":"express uncertainty"}]}'
    result = generate_response(client_with(response('draft'), response(review), response('', finish='length')), [{'role': 'user', 'content': 'x'}])
    assert result.answer == 'draft' and result.status == 'revision_failed_draft_retained'


def test_initial_failure_propagates():
    with pytest.raises(TimeoutError):
        generate_response(client_with(TimeoutError()), [{'role': 'user', 'content': 'x'}])


def test_missing_usage_is_not_reported_as_complete():
    result = generate_response(client_with(response('draft', usage=False)), [{'role': 'user', 'content': 'x'}], reflection=False)
    assert not result.usage_complete


def test_pilot_contract():
    assert len(TASKS) == 20
    for _, _, expected in TASKS:
        assert score(json.dumps({'answer': expected}), expected)
        assert not score('{"answer": null}', expected)
    assert not score('{"answer": true}', 1)
