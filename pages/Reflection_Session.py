"""A narrow, inspectable Sareth reflection session."""
import json
import streamlit as st
from rve.openai_client import openai_client
from rve.session import ReflectionSession

st.set_page_config(page_title='Sareth · Reflection session', page_icon='🧭')
st.title('A reflection you can revise')
st.caption('Bring an everyday dilemma. Interpretations are suggestions you can reject; you decide what fits.')
st.page_link('pages/Recursive_Emergence_Framework.py', label='Back to chat')
st.session_state.setdefault('reflection_session', ReflectionSession())
session = st.session_state.reflection_session
if st.button('Clear this session'):
    st.session_state.reflection_session = ReflectionSession()
    st.rerun()
st.caption('Records stay in this browser session on the app server. Clearing removes the app’s session record; provider retention and downloaded copies are separate.')
mode = st.selectbox('Reflection style', ['plain', 'symbolic', 'direct'],
    format_func=lambda x: {'plain': 'Plain language + review', 'symbolic': 'Optional metaphor + review',
                          'direct': 'Plain language, without review'}[x])
reports = [r for r in session.records if r.kind == 'human_report']
with st.form('report_form', clear_on_submit=True):
    text = st.text_area('Your account', max_chars=8000)
    corrects = st.selectbox('This adds to the conversation, or corrects an earlier account',
                           ['New account'] + [r.id for r in reports])
    submitted = st.form_submit_button('Save account')
if submitted:
    try:
        session.report(text, corrects=None if corrects == 'New account' else corrects)
    except ValueError as exc:
        st.error(str(exc))
    else:
        st.rerun()

if st.button('Reflect on the saved conversation', disabled=not reports):
    try:
        with st.spinner('Preparing a tentative interpretation…'):
            session.interpret(openai_client(), mode=mode)
    except Exception:
        st.error('No new interpretation was published. Your saved account and feedback remain available. The connection, review, or record check could not finish.')

for record in session.records:
    if record.kind == 'human_report':
        st.markdown(f'**Your account · {record.id}**')
        st.text(record.content)
        if record.refs:
            st.caption(f'Corrects {record.refs[0]}; the earlier account remains in the record.')
    elif record.kind == 'interpretation':
        value = json.loads(record.content)
        st.markdown(f'**Tentative interpretation · {record.id}**')
        st.write(value['interpretation'])
        st.caption('Based on your reports: ' + ', '.join(record.refs) + '. Not independent verification.')
        st.write('Other possibilities:')
        for alternative in value['alternatives']:
            st.write('• ' + alternative)
        if value['metaphor']:
            st.write('Optional metaphor: ' + value['metaphor'])
            st.caption('You can discard this image without rejecting your experience.')
        st.write('Possible next step: ' + value['next_step'])
        st.write(value['question'])
        with st.form('feedback_' + record.id, clear_on_submit=True):
            response = st.selectbox('How does this fit?', ['reject', 'revise', 'endorse'])
            feedback = st.text_area('What should change?', max_chars=8000)
            if st.form_submit_button('Save feedback'):
                session.feedback(record.id, response, feedback)
                st.rerun()
    elif record.kind == 'human_feedback':
        value = json.loads(record.content)
        st.markdown(f'**Your feedback on {record.refs[0]} · {value["response"]}**')
        st.text(value['text'])
        st.caption('Agreement records fit; it does not verify the interpretation.')

with st.expander('Record and runtime details'):
    st.caption('Structure and source IDs are checked by software. Meaning and faithfulness can still be wrong. Each click starts a new bounded run; there is no whole-session spend cap.')
    st.json(json.loads(session.export()))
st.download_button('Download session record', session.export(), 'sareth-session.json', 'application/json')
