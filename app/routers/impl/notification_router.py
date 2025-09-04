from typing import Sequence

from app.clients.auth_client import AuthClient
from app.config.bindings import inject
from app.models.notification import Notification
from app.routers.router_wrapper import RouterWrapper
from app.services.notification.notification_service import NotificationService


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