"""Session state helpers. Session state belongs to the current browser session."""
import streamlit as st

def sign_in(result):
    st.session_state['token'] = result['access_token']
    st.session_state['user'] = result['user']

def sign_out():
    for key in ('token', 'user'):
        st.session_state.pop(key, None)
    st.rerun()

def current_user():
    return st.session_state.get('user')
