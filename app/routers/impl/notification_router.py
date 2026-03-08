import os
from typing import Sequence

from fastapi.responses import FileResponse

from app.clients.auth_client import AuthClient
from app.config.bindings import inject
from app.exceptions.not_found_exception import NotFoundException
from app.models.notification import Notification
from app.routers.router_wrapper import RouterWrapper
from app.services.notification.notification_service import NotificationService

SNAPSHOTS_DIR = "/var/lib/notifications-manager/data/snapshots"


class NotificationRouter(RouterWrapper):
    @inject
    def __init__(self, notification_service: NotificationService, auth_client: AuthClient):
        super().__init__(prefix=f"/notification")
        self.notification_service = notification_service
        self.auth_client = auth_client

    def _define_routes(self):
        @self.router.get("/", operation_id="get_all_notifications_with_slash")
        @self.router.get("", operation_id="get_all_notifications_without_slash")
        def get_all_notifications(offset: int = 0) -> Sequence[Notification]:
            return self.notification_service.get_all_paginated(offset=offset)

        @self.router.get("/snapshot/{filename}")
        def get_snapshot(filename: str):
            # Sanitize filename
            safe_name = os.path.basename(filename)
            filepath = os.path.join(SNAPSHOTS_DIR, safe_name)
            if not os.path.exists(filepath):
                raise NotFoundException("Snapshot not found")
            return FileResponse(filepath, media_type="image/jpeg")
