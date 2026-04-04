from abc import ABC, abstractmethod
from typing import Sequence

from app.models.firebase_device_token import FirebaseDeviceToken


class FirebaseDeviceTokenRepository(ABC):
    @abstractmethod
    def upsert(self, token: str) -> FirebaseDeviceToken:
        pass

    @abstractmethod
    def find_all(self) -> Sequence[FirebaseDeviceToken]:
        pass

    @abstractmethod
    def delete(self, token: str) -> None:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass
