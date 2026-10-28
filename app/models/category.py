from datetime import datetime
from sqlalchemy import Boolean,DateTime,String,Text
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db import Base
class TicketCategory(Base):
    __tablename__='ticket_categories'
    id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(80),unique=True,index=True); description:Mapped[str|None]=mapped_column(Text); is_active:Mapped[bool]=mapped_column(Boolean,default=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    tickets=relationship('Ticket',back_populates='category')
