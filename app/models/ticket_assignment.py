from datetime import datetime
from sqlalchemy import Boolean,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db import Base
class TicketAssignment(Base):
    __tablename__='ticket_assignments'
    id:Mapped[int]=mapped_column(primary_key=True); ticket_id:Mapped[int]=mapped_column(ForeignKey('tickets.id'),index=True); engineer_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); assigned_by_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); is_current:Mapped[bool]=mapped_column(Boolean,default=True); assigned_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    ticket=relationship('Ticket',back_populates='assignments'); engineer=relationship('User',foreign_keys=[engineer_id]); assigned_by=relationship('User',foreign_keys=[assigned_by_id])
