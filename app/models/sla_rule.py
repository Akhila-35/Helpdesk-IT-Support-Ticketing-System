from datetime import datetime
from sqlalchemy import DateTime,Enum,Integer,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.db import Base
from app.schemas.enums import Priority
class SLARule(Base):
    __tablename__='sla_rules'; __table_args__=(UniqueConstraint('priority',name='uq_sla_priority'),)
    id:Mapped[int]=mapped_column(primary_key=True); priority:Mapped[Priority]=mapped_column(Enum(Priority),index=True); resolution_hours:Mapped[int]=mapped_column(Integer); created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
