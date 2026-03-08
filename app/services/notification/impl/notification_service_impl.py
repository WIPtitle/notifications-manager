import os
import time
from typing import Sequence

import requests

from app.models.notification import Notification, NotificationInputDto
from app.models.ntfy_credentials import NtfyCredentials
from app.repositories.notification.notification_repository import NotificationRepository
from app.services.notification.notification_service import NotificationService
from app.utils.read_credentials import read_credentials


class NotificationServiceImpl(NotificationService):
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
        self.ntfy_hostname = "ntfy"
        self.ntfy_credentials = read_credentials(os.getenv('NTFY_CREDENTIALS_FILE'))

    def get_ntfy_credentials(self) -> NtfyCredentials:
        return NtfyCredentials(
            user=self.ntfy_credentials['NTFY_READER_USER'],
            password=self.ntfy_credentials['NTFY_READER_PASSWORD'],
            topic=self.ntfy_credentials['NTFY_TOPIC']
        )

    def update_ntfy_credentials(self) -> NtfyCredentials:
        credentials_file = os.getenv('NTFY_CREDENTIALS_FILE')
        old_password = self.ntfy_credentials['NTFY_READER_PASSWORD']

        os.remove(credentials_file)

        new_password = old_password
        while new_password == old_password:
            time.sleep(1)
            try:
                self.ntfy_credentials = read_credentials(credentials_file)
                new_password = self.ntfy_credentials['NTFY_READER_PASSWORD']
            except FileNotFoundError:
                continue

        return NtfyCredentials(
            user=self.ntfy_credentials['NTFY_READER_USER'],
            password=self.ntfy_credentials['NTFY_READER_PASSWORD'],
            topic=self.ntfy_credentials['NTFY_TOPIC']
        )

    def send_notification(self, notification_dto: NotificationInputDto) -> bool:
        notification = Notification.from_dto(notification_dto)
        self.notification_repository.create(notification)

        url = f"http://{self.ntfy_hostname}/{self.ntfy_credentials['NTFY_TOPIC']}"
        auth = (self.ntfy_credentials['NTFY_WRITER_USER'], self.ntfy_credentials['NTFY_WRITER_PASSWORD'])

        headers = {
            "Title": notification.title,
            "Priority": notification.priority,
        }

        response = requests.post(url, data=notification.message, headers=headers, auth=auth)

        return response.status_code == 200

    def save_notification(self, notification_dto: NotificationInputDto, snapshot_filename: str | None = None) -> Notification:
        """Save notification to DB only (no push)."""
        notification = Notification.from_dto(notification_dto)
        notification.snapshot_filename = snapshot_filename
        return self.notification_repository.create(notification)

    def get_all_paginated(self, offset: int) -> Sequence[Notification]:
        return self.notification_repository.find_all_paginated(offset)