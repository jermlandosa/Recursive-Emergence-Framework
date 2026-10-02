from unittest.mock import patch
from pathlib import Path
from streamlit.testing.v1 import AppTest
from rve.reflection import ReflectionResult

PAGE = Path(__file__).resolve().parents[1] / 'pages/Recursive_Emergence_Framework.py'


def test_success_and_reset():
    result = ReflectionResult(answer='A corrected answer.', draft='A draft.',
                              mode='reflection', status='revised', calls=3)
    with patch('rve.openai_client.openai_client', return_value=object()), \
         patch('rve.reflection.generate_response', return_value=result) as generate:
        app = AppTest.from_file(PAGE).run()
        assert not app.exception
        app.chat_input[0].set_value('Hello').run()
        assert not app.exception
        assert app.session_state.chat == [{'role':'user','content':'Hello'},
                                         {'role':'assistant','content':'A corrected answer.'}]
        assert generate.call_args.kwargs['reflection'] is True
        app.button[0].click().run()
        assert not app.exception and app.session_state.chat == []
        assert app.session_state.last_run is None


def test_generation_failure_does_not_commit_turn():
    with patch('rve.openai_client.openai_client', return_value=object()), \
         patch('rve.reflection.generate_response', side_effect=TimeoutError):
        app = AppTest.from_file(PAGE).run()
        app.chat_input[0].set_value('Hello').run()
        assert not app.exception and app.session_state.chat == []
        assert app.error


def test_baseline_toggle_and_degraded_notice():
    result = ReflectionResult(answer='Draft', draft='Draft', mode='reflection',
                              status='critique_failed_draft_retained', calls=2)
    with patch('rve.openai_client.openai_client', return_value=object()), \
         patch('rve.reflection.generate_response', return_value=result) as generate:
        app = AppTest.from_file(PAGE).run()
        app.toggle[0].set_value(False).run()
        app.chat_input[0].set_value('Hello').run()
        assert not app.exception and generate.call_args.kwargs['reflection'] is False
        assert app.warning and app.session_state.last_response == 'Draft'


def test_entrypoint_boots_without_legacy_database(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")
    with patch("rve.ledger.get_session", side_effect=RuntimeError("database unavailable")) as db:
        app = AppTest.from_file(PAGE.parents[1] / "streamlit_app.py").run()
        assert not app.exception
        db.assert_not_called()
