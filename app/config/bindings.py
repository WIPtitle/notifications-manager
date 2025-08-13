import os
import time
from functools import wraps
from typing import Callable, get_type_hints

from rabbitmq_sdk.client.impl.rabbitmq_client_impl import RabbitMQClientImpl
from rabbitmq_sdk.enums.service import Service

from app.consumers.sensor_alarm_consumer import SensorAlarmConsumer
from app.database.database_connector import DatabaseConnector
from app.database.impl.database_connector_impl import DatabaseConnectorImpl
from app.services.notification.impl.notification_service_impl import NotificationServiceImpl
from app.services.notification.notification_service import NotificationService
from app.utils.read_credentials import read_credentials

bindings = { }

database_connector = DatabaseConnectorImpl()

rabbit_credentials = read_credentials(os.getenv('RBBT_CREDENTIALS_FILE'))
rabbitmq_client = RabbitMQClientImpl.from_config(
    host=os.getenv("RABBITMQ_HOSTNAME"), # using container name as host instead of ip
    port=5672,
    username=rabbit_credentials['RABBITMQ_USER'],
    password=rabbit_credentials['RABBITMQ_PASSWORD']
).with_current_service(Service.MAIL_NOTIFICATION)


# Create instances only one time
notification_service = NotificationServiceImpl()

# Consumers
sensor_alarm_consumer = SensorAlarmConsumer(notification_service=notification_service)

# Consume messages with retry if connection fails
while not rabbitmq_client.consume(sensor_alarm_consumer):
    time.sleep(5)

# Put them in an interface -> instance dict so they will be used everytime a dependency is required
bindings[DatabaseConnector] = database_connector

bindings[NotificationService] = notification_service


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