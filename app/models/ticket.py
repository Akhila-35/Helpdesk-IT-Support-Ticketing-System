from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.schemas.enums import Priority, TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(200),
        index=True
    )

    description: Mapped[str] = mapped_column(Text)

    priority: Mapped[Priority | None] = mapped_column(
        Enum(Priority),
        nullable=True,
        index=True
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        default=TicketStatus.OPEN,
        index=True
    )

    requester_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("ticket_categories.id"),
        nullable=True,
        index=True
    )

    sla_breach_deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    requester = relationship(
        "User",
        back_populates="tickets"
    )

    category = relationship(
        "TicketCategory",
        back_populates="tickets"
    )

    comments = relationship(
        "TicketComment",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    assignments = relationship(
        "TicketAssignment",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )