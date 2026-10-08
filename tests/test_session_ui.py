import json
from pathlib import Path
import pytest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from rve.reflection import ReflectionResult

PAGE = Path(__file__).resolve().parents[1] / 'pages/Reflection_Session.py'


@pytest.fixture(autouse=True)
def test_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-not-a-real-key")


def start_page():
    app = AppTest.from_file(PAGE.parents[1] / 'streamlit_app.py').run()
    return app.switch_page('pages/' + PAGE.name).run()


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_full_session_correction_rejection_export_clear():
    payload = json.dumps(dict(interpretation='Perhaps the timing is difficult.',
        alternatives=['You may prefer another plan.'], metaphor='', next_step='List options.',
        question='What does not fit?', source_ids=['r1']))
    result = ReflectionResult(payload, payload, 'reflection', 'reviewed_unchanged', calls=2)
    with patch('rve.openai_client.openai_client', return_value=object()), \
         patch('rve.session.generate_response', return_value=result):
        app = start_page()
        assert not app.exception
        app.text_area[0].set_value('I am unsure about a plan.')
        button(app, 'Save account').click().run()
        button(app, 'Reflect on the saved conversation').click().run()
        assert not app.exception
        app.text_area[1].set_value('No, I just need sleep.')
        button(app, 'Save feedback').click().run()
        app.text_area[0].set_value('I am tired.')
        app.selectbox[1].set_value('r1')
        button(app, 'Save account').click().run()
        records = app.session_state.reflection_session.records
        assert any(r.kind == 'human_feedback' for r in records)
        assert records[-1].refs == ('r1',)
        assert records[0].content == 'I am unsure about a plan.'
        assert not app.exception
        button(app, 'Clear this session').click().run()
        assert not app.session_state.reflection_session.records and not app.exception
