from abc import ABC, abstractmethod
from typing import Sequence

from app.models.notification import Notification, NotificationInputDto
from app.models.ntfy_credentials import NtfyCredentials


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, notification: NotificationInputDto, snapshot_filename: str | None = None) -> bool:
        pass

    @abstractmethod
    def get_ntfy_credentials(self) -> NtfyCredentials:
        pass

    @abstractmethod
    def update_ntfy_credentials(self) -> NtfyCredentials:
        pass

    @abstractmethod
    def save_notification(self, notification: NotificationInputDto, snapshot_filename: str | None = None) -> Notification:
        pass

    @abstractmethod
    def get_all_paginated(self, offset: int) -> Sequence[Notification]:
        pass