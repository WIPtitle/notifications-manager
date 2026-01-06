from functools import wraps
from typing import Callable, get_type_hints

from app.clients.auth_client import AuthClient
from app.database.database_connector import DatabaseConnector
from app.database.impl.database_connector_impl import DatabaseConnectorImpl
from app.repositories.notification.impl.notification_repository_impl import NotificationRepositoryImpl
from app.repositories.notification.notification_repository import NotificationRepository
from app.services.notification.impl.notification_service_impl import NotificationServiceImpl
from app.services.notification.notification_service import NotificationService

bindings = {}

database_connector = DatabaseConnectorImpl()

notification_repository = NotificationRepositoryImpl(database_connector=database_connector)
notification_service = NotificationServiceImpl(notification_repository=notification_repository)

bindings[DatabaseConnector] = database_connector
bindings[NotificationRepository] = notification_repository
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