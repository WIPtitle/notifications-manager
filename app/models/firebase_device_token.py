from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class FirebaseDeviceToken(SQLModel, table=True):
    __tablename__ = "firebase_device_token"
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
