from typing import Sequence

from sqlmodel import select

from app.database.database_connector import DatabaseConnector
from app.models.firebase_device_token import FirebaseDeviceToken
from app.repositories.firebase.firebase_device_token_repository import FirebaseDeviceTokenRepository


class FirebaseDeviceTokenRepositoryImpl(FirebaseDeviceTokenRepository):
    def __init__(self, database_connector: DatabaseConnector):
        self.database_connector = database_connector

    def upsert(self, token: str) -> FirebaseDeviceToken:
        session = self.database_connector.get_new_session()
        existing = session.exec(
            select(FirebaseDeviceToken).where(FirebaseDeviceToken.token == token)
        ).first()
        if existing:
            session.close()
            return existing
        device_token = FirebaseDeviceToken(token=token)
        session.add(device_token)
        session.commit()
        session.refresh(device_token)
        session.close()
        return device_token

    def find_all(self) -> Sequence[FirebaseDeviceToken]:
        session = self.database_connector.get_new_session()
        result = session.exec(select(FirebaseDeviceToken)).all()
        session.close()
        return result

    def delete(self, token: str) -> None:
        session = self.database_connector.get_new_session()
        existing = session.exec(
            select(FirebaseDeviceToken).where(FirebaseDeviceToken.token == token)
        ).first()
        if existing:
            session.delete(existing)
            session.commit()
        session.close()

    def delete_all(self) -> None:
        session = self.database_connector.get_new_session()
        tokens = session.exec(select(FirebaseDeviceToken)).all()
        for token in tokens:
            session.delete(token)
        session.commit()
        session.close()
