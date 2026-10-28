from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id"),
        index=True
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    body: Mapped[str] = mapped_column(
        Text
    )

    channel: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    ticket = relationship(
        "Ticket",
        back_populates="comments"
    )

    author = relationship(
        "User",
        back_populates="comments"
    )