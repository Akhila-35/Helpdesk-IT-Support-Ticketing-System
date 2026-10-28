from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.sla_rule import SLARule
from app.schemas.enums import Priority, TicketStatus


# Default SLA resolution hours.
# These values are inserted into the database during initialization.

DEFAULTS = {
    Priority.CRITICAL: 2,
    Priority.HIGH: 4,
    Priority.MEDIUM: 8,
    Priority.LOW: 24
}


def ensure_sla_rules(db: Session):
    """
    Create default SLA rules if they do not already exist.
    """

    for priority, hours in DEFAULTS.items():

        existing_rule = (
            db.query(SLARule)
            .filter(SLARule.priority == priority)
            .first()
        )

        if existing_rule is None:

            new_rule = SLARule(
                priority=priority,
                resolution_hours=hours
            )

            db.add(new_rule)

    db.commit()


def deadline(
    db: Session,
    priority: Priority,
    start: datetime | None = None
):
    """
    Calculate SLA deadline based on the priority.
    SLA hours are retrieved from the database.
    """

    rule = (
        db.query(SLARule)
        .filter(SLARule.priority == priority)
        .first()
    )

    if rule is None:
        raise HTTPException(
            status_code=400,
            detail=f"No SLA rule configured for priority {priority.value}"
        )

    if rule.resolution_hours <= 0:
        raise HTTPException(
            status_code=400,
            detail="SLA resolution hours must be greater than zero"
        )

    start_time = start or datetime.utcnow()

    return start_time + timedelta(
        hours=rule.resolution_hours
    )


def validate_transition(
    current: TicketStatus,
    new: TicketStatus
):
    """
    Validate ticket status transitions.
    """

    allowed_transitions = {
        TicketStatus.OPEN: {
            TicketStatus.ASSIGNED
        },

        TicketStatus.ASSIGNED: {
            TicketStatus.IN_PROGRESS
        },

        TicketStatus.IN_PROGRESS: {
            TicketStatus.WAITING_FOR_USER,
            TicketStatus.RESOLVED
        },

        TicketStatus.WAITING_FOR_USER: {
            TicketStatus.IN_PROGRESS,
            TicketStatus.RESOLVED
        },

        TicketStatus.RESOLVED: {
            TicketStatus.CLOSED
        },

        TicketStatus.CLOSED: set()
    }

    if new not in allowed_transitions.get(current, set()):

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid status transition: "
                f"{current.value} -> {new.value}"
            )
        )
