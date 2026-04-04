import json
import os

import firebase_admin
from firebase_admin import credentials, messaging

from app.repositories.firebase.firebase_device_token_repository import FirebaseDeviceTokenRepository
from app.services.firebase.firebase_service import FirebaseService

CREDENTIALS_PATH = "/var/lib/notifications-manager/data/firebase_credentials.json"
STALE_TOKEN_CODES = {"registration-token-not-registered", "invalid-argument"}


class FirebaseServiceImpl(FirebaseService):
    def __init__(self, firebase_device_token_repository: FirebaseDeviceTokenRepository):
        self.firebase_device_token_repository = firebase_device_token_repository
        self._firebase_app = None
        self._try_initialize_app()

    def _try_initialize_app(self) -> None:
        if not os.path.exists(CREDENTIALS_PATH):
            return
        try:
            cred = credentials.Certificate(CREDENTIALS_PATH)
            self._firebase_app = firebase_admin.initialize_app(cred)
        except Exception:
            self._firebase_app = None

    def _delete_app(self) -> None:
        if self._firebase_app is not None:
            try:
                firebase_admin.delete_app(self._firebase_app)
            except Exception:
                pass
            self._firebase_app = None

    def is_configured(self) -> bool:
        return os.path.exists(CREDENTIALS_PATH)

    def set_credentials(self, credentials_dict: dict) -> None:
        os.makedirs(os.path.dirname(CREDENTIALS_PATH), exist_ok=True)
        with open(CREDENTIALS_PATH, "w") as f:
            json.dump(credentials_dict, f)
        self._delete_app()
        self._try_initialize_app()

    def delete_credentials(self) -> None:
        if os.path.exists(CREDENTIALS_PATH):
            os.remove(CREDENTIALS_PATH)
        self._delete_app()
        self.firebase_device_token_repository.delete_all()

    def register_device_token(self, token: str) -> None:
        self.firebase_device_token_repository.upsert(token)

    def send_notification(self, title: str, body: str) -> None:
        if self._firebase_app is None:
            return

        tokens = self.firebase_device_token_repository.find_all()
        if not tokens:
            return

        token_strings = [t.token for t in tokens]

        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data={"title": title, "body": body},
            tokens=token_strings,
        )

        response = messaging.send_each_for_multicast(message, app=self._firebase_app)

        for idx, send_response in enumerate(response.responses):
            if not send_response.success:
                error = send_response.exception
                if error is not None:
                    error_code = getattr(error, "code", None)
                    if error_code in STALE_TOKEN_CODES:
                        self.firebase_device_token_repository.delete(token_strings[idx])
