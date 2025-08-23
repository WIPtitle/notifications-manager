from typing import Sequence
from sqlmodel import select

from app.database.database_connector import DatabaseConnector
from app.models.notification import Notification
from app.repositories.notification.notification_repository import NotificationRepository


class NotificationRepositoryImpl(NotificationRepository):
    def __init__(self, database_connector: DatabaseConnector):
        self.database_connector = database_connector

    def create(self, notification: Notification) -> Notification:
        session = self.database_connector.get_new_session()
        session.add(notification)
        session.commit()
        session.refresh(notification)
        session.close()
        return notification

    def find_all_paginated(self, offset: int) -> Sequence[Notification]:
        statement = (
            select(Notification)
            .order_by(Notification.id.desc())
            .offset(offset)
            .limit(20)
        )
        session = self.database_connector.get_new_session()
        result = session.exec(statement).all()
        session.close()
        return result