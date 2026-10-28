from datetime import datetime
from sqlalchemy import Boolean,DateTime,Enum,String
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.db import Base
from app.schemas.enums import UserRole
class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True); full_name:Mapped[str]=mapped_column(String(120)); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(512)); role:Mapped[UserRole]=mapped_column(Enum(UserRole),default=UserRole.REQUESTER); is_active:Mapped[bool]=mapped_column(Boolean,default=True); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    tickets=relationship('Ticket',back_populates='requester'); comments=relationship('TicketComment',back_populates='author')
