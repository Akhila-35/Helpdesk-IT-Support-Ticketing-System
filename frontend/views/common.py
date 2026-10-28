"""Reusable dashboard views."""
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from services.api_client import get, post, APIError

def load_tickets():
    return get('/tickets')

def readable(value):
    return str(value or 'Not assigned').replace('_', ' ').title()

def metrics(tickets):
    counts = [len(tickets), sum(t['status'] == 'open' for t in tickets),
              sum(t['status'] == 'in_progress' for t in tickets),
              sum(t['status'] == 'resolved' for t in tickets)]
    for column, label, value in zip(st.columns(4), ['Total', 'Open', 'In progress', 'Resolved'], counts):
        column.metric(label, value)

def ticket_table(tickets):
    if not tickets:
        st.info('No tickets found.')
        return
    status_filter = st.selectbox('Filter by status', ['All'] + sorted(set(t['status'] for t in tickets)))
    rows = [t for t in tickets if status_filter == 'All' or t['status'] == status_filter]
    data = [{'ID': t['id'], 'Title': t['title'], 'Status': readable(t['status']),
             'Priority': readable(t['priority']), 'Category ID': t['category_id'] or '—',
             'Created': str(t['created_at'])[:16]} for t in rows]
    st.dataframe(pd.DataFrame(data), hide_index=True, width=True)

def choose_ticket(tickets, key):
    if not tickets:
        st.info('No tickets available for this action.')
        return None
    ticket_id = st.selectbox('Select ticket', [t['id'] for t in tickets],
                             format_func=lambda i: f'#{i} — {next(t["title"] for t in tickets if t["id"] == i)}', key=key)
    return next(t for t in tickets if t['id'] == ticket_id)

def ticket_details(ticket):
    st.markdown(f'**Description:** {ticket["description"]}')
    st.write('Status:', readable(ticket['status']))
    st.write('Priority:', readable(ticket['priority']))
    st.write('Requester ID:', ticket['requester_id'])
    st.write('Category ID:', ticket['category_id'] or 'Not assigned')
    st.write('SLA deadline (UTC):', ticket['sla_breach_deadline'] or 'Not set')

def notifications():
    st.subheader("Notifications")

    items = get("/notifications")

    if items is None:
        st.error("Unable to load notifications.")
        return

    if not items:
        st.info("No notifications.")
        return

    for item in items:

        notification_id = item["id"]
        title = item.get("title") or "Notification"
        message = item.get("message") or "No message available."
        is_read = item.get("is_read", False)
        created_at = item.get("created_at", "")

        with st.container(border=True):

            if is_read:
                st.markdown(f"**{title}**")
            else:
                st.markdown(f"**{title}** · 🔵 New")

            st.write(message)

            if created_at:
                st.caption(str(created_at)[:19] + " UTC")

            if not is_read:

                if st.button(
                    "Mark as read",
                    key=f"notification_{notification_id}"
                ):

                    result = post(
                        f"/notifications/{notification_id}/read"
                    )

                    if result is not None:
                        st.rerun()
                    else:
                        st.error("Unable to mark notification as read.")

def sla_monitor(tickets):
    st.subheader('SLA Monitor')
    now = datetime.now(timezone.utc)
    rows = []
    for ticket in tickets:
        if not ticket['sla_breach_deadline']:
            continue
        deadline = datetime.fromisoformat(ticket['sla_breach_deadline'].replace('Z', '+00:00'))
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if ticket['status'] in ('resolved', 'closed'):
            state = 'Completed (deadline comparison not shown)'
        elif deadline < now:
            state = 'Overdue'
        else:
            state = 'Within deadline'
        rows.append({'Ticket': ticket['id'], 'Priority': readable(ticket['priority']),
                     'Deadline (UTC)': deadline.strftime('%Y-%m-%d %H:%M'), 'SLA view': state})
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width=True)
    else:
        st.info('No classified tickets with SLA deadlines.')
    st.caption('This is a deadline monitor, not a historical SLA compliance report.')

def ticket_messages(ticket_id, channel=None):
    """
    Display ticket messages and allow the current user
    to send a message.

    Requesters and engineers do not choose a channel.
    Admin selects the conversation through the dashboard.
    """

    st.subheader("Messages")

    params = {}

    if channel is not None:
        params["channel"] = channel

    try:
        messages = get(
            f"/tickets/{ticket_id}/comments",
            params=params
        )

    except APIError as error:
        st.error(f"Unable to load messages: {error}")
        return

    if not messages:
        st.info("No messages yet. Start the conversation below.")

    for message in messages:

        with st.container(border=True):

            st.write(message["body"])

            st.caption(
                f"User ID: {message['author_id']} | "
                f"Sent: {message['created_at']}"
            )

    with st.form(
        key=f"message_form_{ticket_id}_{channel}"
    ):

        message_body = st.text_area(
            "Write a message",
            max_chars=10000,
            key=f"message_body_{ticket_id}_{channel}"
        )

        send_message = st.form_submit_button(
            "Send Message"
        )

    if send_message:

        if not message_body.strip():
            st.warning("Please enter a message.")
            return

        try:
            post(
                f"/tickets/{ticket_id}/comments",
                payload={
                    "body": message_body.strip()
                },
                params=params
            )

            st.toast("Message sent successfully!")
            st.rerun()

        except APIError as error:
            st.error(f"Unable to send message: {error}")
