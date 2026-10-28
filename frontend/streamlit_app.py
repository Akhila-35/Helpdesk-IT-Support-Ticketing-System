"""Application entry point: login and role-based navigation."""
import streamlit as st
from services.api_client import get, APIError
from utils.session import current_user, sign_out
from views.auth import show_auth
from views.requester import show_requester
from views.engineer import show_engineer
from views.admin import show_admin

st.set_page_config(page_title='IT Support Helpdesk', page_icon='🎫', layout='wide')
st.set_option(
    "client.showSidebarNavigation",
    False
)
st.markdown('''<style>
.block-container {padding-top: 2rem; max-width: 1250px;}
div[data-testid="stMetric"] {border: 1px solid #dce2e8; padding: 14px; border-radius: 9px;}
</style>''', unsafe_allow_html=True)

if not current_user():
    show_auth()
    st.stop()

try:
    user = get('/users/me')
    st.session_state['user'] = user
except APIError as error:
    st.error(f'Your session could not be verified: {error}')
    if st.button('Return to login'):
        sign_out()
    st.stop()

role = user['role']
menu = {
    'requester': ['Dashboard', 'Create Ticket', 'Ticket Details', 'Notifications'],
    'admin': ['Dashboard', 'Manage Tickets', 'SLA Monitor', 'Categories', 'Engineers', 'Notifications'],
    'engineer': ['Dashboard', 'Update Progress', 'SLA Monitor', 'Notifications'],
}
if role not in menu:
    st.error('Unknown user role.')
    st.stop()

with st.sidebar:
    st.header("IT Support Helpdesk")

    st.write(user["full_name"])

    st.caption(f"Role: {role.title()}")

    section = st.radio(
        "Navigation",
        menu[role],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("Log out", width="stretch"):
        sign_out()

try:
    if role == 'requester':
        show_requester(section)
    elif role == 'admin':
        show_admin(section)
    elif role == 'engineer':
        show_engineer(section)
except APIError as error:
    st.error(f'API error: {error}')
