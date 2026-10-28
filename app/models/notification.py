from datetime import datetime
from sqlalchemy import Boolean,DateTime,ForeignKey,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db import Base
class Notification(Base):
    __tablename__='notifications'
    id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id'),index=True); ticket_id:Mapped[int|None]=mapped_column(ForeignKey('tickets.id'),nullable=True,index=True); title:Mapped[str]=mapped_column(String(200)); message:Mapped[str]=mapped_column(Text); is_read:Mapped[bool]=mapped_column(Boolean,default=False); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    ticket=relationship('Ticket',back_populates='notifications'); user=relationship('User')
