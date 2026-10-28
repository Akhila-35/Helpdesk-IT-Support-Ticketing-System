"""Engineer dashboard. Only allowed status transitions are displayed."""
import streamlit as st
from services.api_client import patch
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

ALLOWED = {
    'assigned': ['in_progress'],
    'in_progress': ['waiting_for_user', 'resolved'],
    'waiting_for_user': ['in_progress', 'resolved'],
}

def show_engineer(section):
    if section == 'Notifications':
        notifications()
        return
    tickets = load_tickets()
    if section == 'Dashboard':
        st.title('Engineer Dashboard')
        metrics(tickets)
        ticket_table(tickets)
    elif section == 'Update Progress':
        st.title('Update Ticket Progress')
        ticket = choose_ticket(tickets, 'engineer_ticket')
        if ticket:
            ticket_details(ticket)
            choices = ALLOWED.get(ticket['status'], [])
            if choices:
                status = st.selectbox('New status', choices, format_func=lambda s: s.replace('_', ' ').title())
                if st.button('Save status', type='primary'):
                    patch(f'/tickets/{ticket["id"]}/status', {'status': status})
                    st.success('Ticket status updated.')
                    st.rerun()
            else:
                st.info('No status changes available for this ticket.')
            st.divider()

            st.subheader("Communication with Admin")

            ticket_messages(
                ticket_id=ticket["id"]
            )
    elif section == 'SLA Monitor':
        st.title('My SLA Deadlines')
        sla_monitor(tickets)
