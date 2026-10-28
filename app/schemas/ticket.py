from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import Priority, TicketStatus

from typing import Literal


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=1)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    priority: Priority | None
    status: TicketStatus
    requester_id: int
    category_id: int | None
    sla_breach_deadline: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AssignRequest(BaseModel):
    engineer_id: int = Field(gt=0)


class AssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    engineer_id: int
    assigned_by_id: int
    is_current: bool
    assigned_at: datetime

CommentChannel = Literal[
    "requester_admin",
    "admin_engineer"
]

class CommentCreate(BaseModel):
    body: str = Field(
        min_length=1,
        max_length=10000
    )


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author_id: int
    body: str
    channel: CommentChannel | None
    created_at: datetime

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool


class StatusUpdate(BaseModel):
    status: TicketStatus
class TicketClassify(BaseModel):
    category_id: int = Field(gt=0)
    priority: Priority