from fastapi import Request

from app.clients.auth_client import AuthClient
from app.config.bindings import inject
from app.exceptions.authorization_exception import AuthorizationException
from app.routers.router_wrapper import RouterWrapper
from app.services.notification.notification_service import NotificationService


class NtfyConfigRouter(RouterWrapper):
    @inject
    def __init__(self, notification_service: NotificationService, auth_client: AuthClient):
        super().__init__(prefix=f"/ntfy-config")
        self.notification_service = notification_service
        self.auth_client = auth_client

    def _define_routes(self):
        @self.router.get("/credentials")
        def get_ntfy_credentials():
            return self.notification_service.get_ntfy_credentials()

        @self.router.put("/credentials")
        async def update_ntfy_credentials(request: Request):
            token = request.headers.get("Authorization")
            user = await self.auth_client.get_authenticated_user(token)
            if user is None or "UPDATE_NOTIFICATIONS_CONFIG" not in user.permissions:
                raise AuthorizationException("Not authorized")
            return self.notification_service.update_ntfy_credentials()