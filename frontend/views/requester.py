"""Requester dashboard."""
import streamlit as st
from services.api_client import post
from views.common import (
    load_tickets,
    metrics,
    ticket_table,
    choose_ticket,
    ticket_details,
    notifications,
    ticket_messages
)

def show_requester(section):
    if section == 'Notifications':
        notifications()
        return
    tickets = load_tickets()
    if section == 'Dashboard':
        st.title('Requester Dashboard')
        metrics(tickets)
        st.subheader('My tickets')
        ticket_table(tickets)
    elif section == 'Create Ticket':
        st.title('Create Support Ticket')
        st.caption('The admin will select the category and priority after reviewing your request.')
        with st.form('new_ticket'):
            title = st.text_input('Issue title', max_chars=200)
            description = st.text_area('Describe the problem')
            submit = st.form_submit_button('Submit ticket', type='primary')
        if submit:
            if len(title.strip()) < 3 or not description.strip():
                st.warning('Provide a title of at least 3 characters and a description.')
            else:
                result = post('/tickets', {'title': title.strip(), 'description': description.strip()})
                st.success(f'Ticket #{result["id"]} created successfully.')
    elif section == "Ticket Details":

        st.title("My Ticket Details")

        ticket = choose_ticket(
            tickets,
            "requester_ticket"
        )

        if ticket:

            ticket_details(ticket)

            st.divider()

            st.subheader("Communication with Admin")

            ticket_messages(
                ticket_id=ticket["id"]
            )
