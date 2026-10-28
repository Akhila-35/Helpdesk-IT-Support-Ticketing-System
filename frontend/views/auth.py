"""Authentication forms."""
import streamlit as st
from services.api_client import post, APIError
from utils.session import sign_in

def show_auth():
    st.title('IT Support Helpdesk')
    st.caption('Submit, manage and resolve support tickets.')
    login_tab, register_tab = st.tabs(['Login', 'Create requester account'])
    with login_tab:
        with st.form('login_form'):
            email = st.text_input('Email address')
            password = st.text_input('Password', type='password')
            submitted = st.form_submit_button('Log in', type='primary')
        if submitted:
            try:
                result = post('/auth/login/json', {'email': email.strip(), 'password': password}, authenticated=False)
                sign_in(result)
                st.rerun()
            except APIError as error:
                st.error(str(error))
    with register_tab:
        st.info('New accounts have the Requester role. An admin manages other roles.')
        with st.form('register_form'):
            full_name = st.text_input('Full name')
            new_email = st.text_input('Email', key='register_email')
            new_password = st.text_input('Password (at least 8 characters)', type='password', key='register_password')
            confirm = st.text_input('Confirm password', type='password')
            create = st.form_submit_button('Register')
        if create:
            if new_password != confirm:
                st.error('Passwords do not match.')
            else:
                try:
                    post('/auth/register', {'full_name': full_name.strip(), 'email': new_email.strip(), 'password': new_password}, authenticated=False)
                    st.success('Account created. Switch to Login to continue.')
                except APIError as error:
                    st.error(str(error))
