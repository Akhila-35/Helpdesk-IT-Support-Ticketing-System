"""Admin ticket management and reporting."""
import streamlit as st
from services.api_client import get, post, patch
from views.common import (
    load_tickets,
    metrics,
    ticket_table,
    choose_ticket,
    ticket_details,
    notifications,
    sla_monitor,
    ticket_messages
)

PRIORITIES = ['low', 'medium', 'high', 'critical']

def show_admin(section):
    if section == 'Notifications':
        notifications()
        return
    tickets = load_tickets()
    if section == 'Dashboard':
        st.title('Admin Dashboard')
        metrics(tickets)
        ticket_table(tickets)
    elif section == 'Manage Tickets':
        st.title('Manage Tickets')
        ticket = choose_ticket(tickets, 'admin_ticket')
        if not ticket:
            return
        ticket_details(ticket)
        st.divider()
        if ticket['status'] == 'open' and ticket['category_id'] is None:
            st.subheader('Classify ticket')
            categories = get('/categories')
            if not categories:
                st.warning('Create a category before classifying tickets.')
            else:
                with st.form(f'classify_{ticket["id"]}'):
                    category_id = st.selectbox('Category', [c['id'] for c in categories],
                                               format_func=lambda i: next(c['name'] for c in categories if c['id'] == i))
                    priority = st.selectbox('Priority', PRIORITIES)
                    classify = st.form_submit_button('Save classification')
                if classify:
                    patch(f'/tickets/{ticket["id"]}/classify', {'category_id': category_id, 'priority': priority})
                    st.success('Ticket classified and SLA deadline set.')
                    st.rerun()
        if ticket['status'] in ('open', 'assigned') and ticket['category_id'] is not None and ticket['priority'] is not None:
            st.subheader('Assign engineer')
            engineers = get('/users/engineers')
            if not engineers:
                st.info('No active engineers are available.')
            else:
                with st.form(f'assign_{ticket["id"]}'):
                    engineer_id = st.selectbox('Engineer', [u['id'] for u in engineers],
                                                format_func=lambda i: next(u['full_name'] for u in engineers if u['id'] == i))
                    assign = st.form_submit_button('Assign engineer')
                if assign:
                    post(f'/tickets/{ticket["id"]}/assign', {'engineer_id': engineer_id})
                    st.success('Engineer assigned; ticket status is now ASSIGNED.')
                    st.rerun()
        if ticket['status'] == 'resolved':
            st.subheader('Close resolved ticket')
            if st.button('Close ticket', type='primary'):
                patch(f'/tickets/{ticket["id"]}/status', {'status': 'closed'})
                st.success('Ticket closed.')
                st.rerun()
            
        
        st.divider()

        st.subheader("Ticket Communication")

        requester_tab, engineer_tab = st.tabs(
            [
                "Requester Conversation",
                "Engineer Conversation"
            ]
        )

        with requester_tab:

            ticket_messages(
                ticket_id=ticket["id"],
                channel="requester_admin"
            )

        with engineer_tab:

            ticket_messages(
                ticket_id=ticket["id"],
                channel="admin_engineer"
            )
    elif section == 'SLA Monitor':
        st.title('SLA Monitoring')
        sla_monitor(tickets)
    elif section == 'Categories':
        st.title('Ticket Categories')
        categories = get('/categories')
        for category in categories:
            st.write(f'**{category["name"]}** — {category.get("description") or "No description"}')
        with st.form('create_category'):
            name = st.text_input('New category name')
            description = st.text_area('Description')
            create = st.form_submit_button('Add category')
        if create:
            post('/categories', {'name': name.strip(), 'description': description.strip() or None})
            st.success('Category created.')
            st.rerun()
    elif section == 'Engineers':
        st.title('Active Engineers')
        engineers = get('/users/engineers')
        if engineers:
            for engineer in engineers:
                st.write(f'{engineer["full_name"]} — {engineer["email"]}')
        else:
            st.info('No active engineers.')
        st.caption('The current backend does not provide an admin user-list endpoint. Role changes require a known user ID and are not exposed in this interface.')
