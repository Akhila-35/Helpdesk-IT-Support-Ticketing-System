from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_roles
)

from app.models.ticket import Ticket
from app.models.category import TicketCategory
from app.models.user import User
from app.models.ticket_assignment import TicketAssignment
from app.models.comment import TicketComment

from app.schemas.ticket import (
    TicketCreate,
    TicketRead,
    AssignRequest,
    AssignmentRead,
    CommentCreate,
    CommentRead,
    StatusUpdate,
    TicketClassify
)

from app.schemas.enums import (
    UserRole,
    Priority,
    TicketStatus
)

from app.services.sla import deadline,validate_transition
from app.services.notifications import notify


router = APIRouter()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def get_ticket(ticket_id: int, db: Session):

    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return ticket


def get_current_assignment(ticket_id: int, db: Session):

    return (
        db.query(TicketAssignment)
        .filter(
            TicketAssignment.ticket_id == ticket_id,
            TicketAssignment.is_current.is_(True)
        )
        .first()
    )


def can_view(ticket: Ticket, user: User, db: Session):

    if user.role == UserRole.ADMIN:
        return True

    if user.role == UserRole.REQUESTER:

        if ticket.requester_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own tickets"
            )

        return True

    if user.role == UserRole.ENGINEER:

        assignment = get_current_assignment(ticket.id, db)

        if assignment is None or assignment.engineer_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access tickets assigned to you"
            )

        return True

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )
def check_message_permission(
    ticket: Ticket,
    current_user: User,
    channel: str,
    db: Session
):

    allowed_channels = (
        "requester_admin",
        "admin_engineer"
    )

    if channel not in allowed_channels:
        raise HTTPException(
            status_code=400,
            detail="Invalid communication channel"
        )

    if current_user.role == UserRole.ADMIN:
        return

    if channel == "requester_admin":

        if (
            current_user.role == UserRole.REQUESTER
            and ticket.requester_id == current_user.id
        ):
            return

    if channel == "admin_engineer":

        if current_user.role == UserRole.ENGINEER:

            assignment = get_current_assignment(
                ticket.id,
                db
            )

            if (
                assignment is not None
                and assignment.engineer_id == current_user.id
            ):
                return

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this conversation"
    )

def get_message_channel(
    current_user: User,
    requested_channel: str | None = None
) -> str:

    if current_user.role == UserRole.REQUESTER:
        return "requester_admin"

    if current_user.role == UserRole.ENGINEER:
        return "admin_engineer"

    if current_user.role == UserRole.ADMIN:

        if requested_channel not in (
            "requester_admin",
            "admin_engineer"
        ):
            raise HTTPException(
                status_code=400,
                detail="Admin must select a valid conversation"
            )

        return requested_channel

    raise HTTPException(
        status_code=403,
        detail="Access denied"
    )
# --------------------------------------------------
# CREATE TICKET
# ONLY REQUESTER
# --------------------------------------------------

@router.post(
    "",
    response_model=TicketRead,
    status_code=201
)
def create(
    data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("requester"))
):

    title = data.title.strip()
    description = data.description.strip()

    if not title or not description:
        raise HTTPException(
            status_code=400,
            detail="Title and description cannot be empty"
        )

    now = datetime.utcnow()

    new_ticket = Ticket(
        title=title,
        description=description,
        requester_id=current_user.id,
        status=TicketStatus.OPEN,
        priority=None,
        category_id=None,
        sla_breach_deadline=None,
        created_at=now,
        updated_at=now
    )

    db.add(new_ticket)

    db.commit()

    db.refresh(new_ticket)

    return new_ticket


# --------------------------------------------------
# LIST TICKETS
# ROLE BASED VISIBILITY
# --------------------------------------------------

@router.get(
    "",
    response_model=list[TicketRead]
)
def list_tickets(
    status: TicketStatus | None = Query(None),
    priority: Priority | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(Ticket)

    if current_user.role == UserRole.REQUESTER:

        query = query.filter(
            Ticket.requester_id == current_user.id
        )

    elif current_user.role == UserRole.ENGINEER:

        query = query.join(
            TicketAssignment,
            TicketAssignment.ticket_id == Ticket.id
        ).filter(
            TicketAssignment.engineer_id == current_user.id,
            TicketAssignment.is_current.is_(True)
        )

    elif current_user.role != UserRole.ADMIN:

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    if status is not None:
        query = query.filter(Ticket.status == status)

    if priority is not None:
        query = query.filter(Ticket.priority == priority)

    return query.order_by(
        Ticket.created_at.desc()
    ).all()


# --------------------------------------------------
# GET SINGLE TICKET
# --------------------------------------------------

@router.get(
    "/{ticket_id}",
    response_model=TicketRead
)
def get(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ticket = get_ticket(ticket_id, db)

    can_view(ticket, current_user, db)

    return ticket
# --------------------------------------------------
# CLASSIFY TICKET
# ONLY ADMIN
# --------------------------------------------------

@router.patch(
    "/{ticket_id}/classify",
    response_model=TicketRead
)
def classify_ticket(
    ticket_id: int,
    data: TicketClassify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    # Get the ticket
    ticket = get_ticket(ticket_id, db)

    # Only OPEN tickets can be classified
    if ticket.status != TicketStatus.OPEN:
        raise HTTPException(
            status_code=400,
            detail="Only OPEN tickets can be classified"
        )

    # Check whether category exists
    category = db.get(TicketCategory, data.category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check whether category is active
    if not category.is_active:
        raise HTTPException(
            status_code=400,
            detail="Selected category is inactive"
        )

    # Get current time
    current_time = datetime.utcnow()

    # Calculate SLA deadline
    sla_deadline = deadline(
        db=db,
        priority=data.priority,
        start=current_time
    )

    # Update ticket
    ticket.category_id = category.id
    ticket.priority = data.priority
    ticket.sla_breach_deadline = sla_deadline
    ticket.updated_at = current_time

    # Save changes
    db.commit()
    db.refresh(ticket)

    return ticket

# --------------------------------------------------
# ASSIGN ENGINEER
# ONLY ADMIN
# --------------------------------------------------

@router.post(
    "/{ticket_id}/assign",
    response_model=AssignmentRead
)
def assign(
    ticket_id: int,
    data: AssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):

    ticket = get_ticket(ticket_id, db)

    engineer = db.get(User, data.engineer_id)

    if (
        engineer is None
        or not engineer.is_active
        or engineer.role != UserRole.ENGINEER
    ):
        raise HTTPException(
            status_code=400,
            detail="Target user must be an active engineer"
        )

    if ticket.category_id is None or ticket.priority is None:
        raise HTTPException(
            status_code=400,
            detail="Admin must set category and priority before assigning an engineer"
        )

    if ticket.status not in (
        TicketStatus.OPEN,
        TicketStatus.ASSIGNED
    ):
        raise HTTPException(
            status_code=400,
            detail="Only open or assigned tickets can be assigned"
        )

    existing_assignments = (
        db.query(TicketAssignment)
        .filter(
            TicketAssignment.ticket_id == ticket.id,
            TicketAssignment.is_current.is_(True)
        )
        .all()
    )

    for assignment in existing_assignments:
        assignment.is_current = False

    new_assignment = TicketAssignment(
        ticket_id=ticket.id,
        engineer_id=engineer.id,
        assigned_by_id=current_user.id,
        is_current=True
    )

    ticket.status = TicketStatus.ASSIGNED
    ticket.updated_at = datetime.utcnow()

    db.add(new_assignment)

    notification = notify(
        db,
        engineer.id,
        "Ticket Assigned",
        f"Ticket #{ticket.id} has been assigned to you.",
        ticket.id
    )

    db.add(notification)

    db.commit()

    db.refresh(new_assignment)

    return new_assignment


# --------------------------------------------------
# ADD COMMENT
# REQUESTER / ASSIGNED ENGINEER / ADMIN
# --------------------------------------------------

@router.post(
    "/{ticket_id}/comments",
    response_model=CommentRead,
    status_code=201
)

def comment(
    ticket_id: int,
    data: CommentCreate,
    channel: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ticket = get_ticket(ticket_id, db)

    selected_channel = get_message_channel(
        current_user,
        channel
    )

    check_message_permission(
        ticket,
        current_user,
        selected_channel,
        db
    )

    comment_body = data.body.strip()

    if not comment_body:
        raise HTTPException(
            status_code=400,
            detail="Comment cannot be empty"
        )

    new_comment = TicketComment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        body=comment_body,
        channel=selected_channel
    )

    db.add(new_comment)

    notification_user_ids = set()

    if selected_channel == "requester_admin":

        if current_user.role == UserRole.ADMIN:
            notification_user_ids.add(ticket.requester_id)

        else:
            admins = (
                db.query(User)
                .filter(
                    User.role == UserRole.ADMIN,
                    User.is_active.is_(True)
                )
                .all()
            )

            for admin in admins:
                notification_user_ids.add(admin.id)

    elif selected_channel == "admin_engineer":

        assignment = get_current_assignment(
            ticket.id,
            db
        )

        if current_user.role == UserRole.ADMIN:

            if assignment is not None:
                notification_user_ids.add(
                    assignment.engineer_id
                )

        else:
            admins = (
                db.query(User)
                .filter(
                    User.role == UserRole.ADMIN,
                    User.is_active.is_(True)
                )
                .all()
            )

            for admin in admins:
                notification_user_ids.add(admin.id)

    notification_user_ids.discard(current_user.id)

    for user_id in notification_user_ids:

        notification = notify(
            db,
            user_id,
            "New Ticket Message",
            f"New message for ticket #{ticket.id}:\n\n{comment_body}",
            ticket.id
        )

        db.add(notification)

    db.commit()
    db.refresh(new_comment)

    return new_comment
# --------------------------------------------------
# VIEW COMMENTS
# --------------------------------------------------
@router.get(
    "/{ticket_id}/comments",
    response_model=list[CommentRead]
)
def comments(
    ticket_id: int,
    channel: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ticket = get_ticket(ticket_id, db)

    selected_channel = get_message_channel(
        current_user,
        channel
    )

    check_message_permission(
        ticket,
        current_user,
        selected_channel,
        db
    )

    return (
        db.query(TicketComment)
        .filter(
            TicketComment.ticket_id == ticket.id,
            TicketComment.channel == selected_channel
        )
        .order_by(
            TicketComment.created_at,
            TicketComment.id
        )
        .all()
    )

# --------------------------------------------------
# UPDATE TICKET STATUS
# ENGINEER RESOLVES
# ADMIN CLOSES
# --------------------------------------------------

@router.patch(
    "/{ticket_id}/status",
    response_model=TicketRead
)
def update_status(
    ticket_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    ticket = get_ticket(ticket_id, db)

    can_view(ticket, current_user, db)

    new_status = data.status

    # Requesters cannot update status

    if current_user.role == UserRole.REQUESTER:

        raise HTTPException(
            status_code=403,
            detail="Requesters cannot update ticket status"
        )

    # Only admin can close resolved tickets

    if new_status == TicketStatus.CLOSED:

        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="Only admin can close tickets"
            )

        if ticket.status != TicketStatus.RESOLVED:
            raise HTTPException(
                status_code=400,
                detail="Only resolved tickets can be closed"
            )

    # Only assigned engineers can update work progress

    elif new_status in (
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_FOR_USER,
        TicketStatus.RESOLVED
    ):

        if current_user.role != UserRole.ENGINEER:
            raise HTTPException(
                status_code=403,
                detail="Only assigned engineers can update work progress"
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="This status cannot be set manually"
        )

    # Validate allowed status transitions

    validate_transition(ticket.status, new_status)

    now = datetime.utcnow()

    ticket.status = new_status
    ticket.updated_at = now

    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = now

    if new_status == TicketStatus.CLOSED:
        ticket.closed_at = now

    # Notify requester when ticket is resolved

    if new_status == TicketStatus.RESOLVED:

        notification = notify(
            db,
            ticket.requester_id,
            "Ticket Resolved",
            f"Your ticket #{ticket.id} has been resolved.",
            ticket.id
        )

        db.add(notification)

    # Notify requester when ticket is closed

    if new_status == TicketStatus.CLOSED:

        notification = notify(
            db,
            ticket.requester_id,
            "Ticket Closed",
            f"Your ticket #{ticket.id} has been closed.",
            ticket.id
        )

        db.add(notification)

    db.commit()

    db.refresh(ticket)

    return ticket