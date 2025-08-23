from abc import ABC, abstractmethod
from typing import Sequence

from app.models.notification import Notification


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    def find_all_paginated(self, offset: int) -> Sequence[Notification]:
        pass