from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class NotificationInputDto(SQLModel):
    title: str
    priority: str
    message: Optional[str] = None


class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    priority: str
    created_at: datetime = None
    message: Optional[str] = None
    snapshot_filename: Optional[str] = Field(default=None)

    @classmethod
    def from_dto(cls, dto: NotificationInputDto):
        return cls(
            title=dto.title,
            priority=dto.priority,
            created_at=datetime.now(tz=timezone.utc),
            message=dto.message
        )