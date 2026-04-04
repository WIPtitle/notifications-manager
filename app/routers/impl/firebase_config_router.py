from fastapi import Request

from app.clients.auth_client import AuthClient
from app.config.bindings import inject
from app.exceptions.authorization_exception import AuthorizationException
from app.exceptions.bad_request_exception import BadRequestException
from app.routers.router_wrapper import RouterWrapper
from app.services.firebase.firebase_service import FirebaseService


class FirebaseConfigRouter(RouterWrapper):
    @inject
    def __init__(self, firebase_service: FirebaseService, auth_client: AuthClient):
        super().__init__(prefix="/firebase-config")
        self.firebase_service = firebase_service
        self.auth_client = auth_client

    def _define_routes(self):
        @self.router.get("/status")
        def get_status():
            return {"configured": self.firebase_service.is_configured()}

        @self.router.post("/credentials")
        async def set_credentials(request: Request):
            token = request.headers.get("Authorization")
            user = await self.auth_client.get_authenticated_user(token)
            if user is None or "UPDATE_NOTIFICATIONS_CONFIG" not in user.permissions:
                raise AuthorizationException("Not authorized")
            try:
                body = await request.json()
            except Exception:
                raise BadRequestException("Invalid JSON body")
            self.firebase_service.set_credentials(body)
            return {"configured": True}

        @self.router.delete("/credentials")
        async def delete_credentials(request: Request):
            token = request.headers.get("Authorization")
            user = await self.auth_client.get_authenticated_user(token)
            if user is None or "UPDATE_NOTIFICATIONS_CONFIG" not in user.permissions:
                raise AuthorizationException("Not authorized")
            self.firebase_service.delete_credentials()
            return {"configured": False}

        @self.router.post("/device-token")
        async def register_device_token(request: Request):
            try:
                body = await request.json()
                token = body.get("token")
            except Exception:
                raise BadRequestException("Invalid JSON body")
            if not token:
                raise BadRequestException("Missing 'token' field")
            self.firebase_service.register_device_token(token)
            return {"registered": True}
