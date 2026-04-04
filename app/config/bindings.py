from functools import wraps
from typing import Callable, get_type_hints

from app.clients.auth_client import AuthClient
from app.database.database_connector import DatabaseConnector
from app.database.impl.database_connector_impl import DatabaseConnectorImpl
from app.repositories.firebase.firebase_device_token_repository import FirebaseDeviceTokenRepository
from app.repositories.firebase.impl.firebase_device_token_repository_impl import FirebaseDeviceTokenRepositoryImpl
from app.repositories.notification.impl.notification_repository_impl import NotificationRepositoryImpl
from app.repositories.notification.notification_repository import NotificationRepository
from app.services.firebase.firebase_service import FirebaseService
from app.services.firebase.impl.firebase_service_impl import FirebaseServiceImpl
from app.services.notification.impl.notification_service_impl import NotificationServiceImpl
from app.services.notification.notification_service import NotificationService

bindings = {}

database_connector = DatabaseConnectorImpl()

notification_repository = NotificationRepositoryImpl(database_connector=database_connector)
firebase_device_token_repository = FirebaseDeviceTokenRepositoryImpl(database_connector=database_connector)

firebase_service = FirebaseServiceImpl(firebase_device_token_repository=firebase_device_token_repository)
notification_service = NotificationServiceImpl(
    notification_repository=notification_repository,
    firebase_service=firebase_service,
)

bindings[DatabaseConnector] = database_connector
bindings[NotificationRepository] = notification_repository
bindings[FirebaseDeviceTokenRepository] = firebase_device_token_repository
bindings[FirebaseService] = firebase_service
bindings[NotificationService] = notification_service
bindings[AuthClient] = AuthClient()


def resolve(interface):
    implementation = bindings[interface]
    if implementation is None:
        raise ValueError(f"No binding found for {interface}")
    return implementation


def inject(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        type_hints = get_type_hints(func)
        for name, param_type in type_hints.items():
            if param_type in bindings:
                kwargs[name] = resolve(param_type)
        return func(*args, **kwargs)
    return wrapper
