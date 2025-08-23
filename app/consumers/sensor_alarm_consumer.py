from typing import Type

from rabbitmq_sdk.consumer.base_consumer import BaseConsumer
from rabbitmq_sdk.enums.event import Event
from rabbitmq_sdk.event.base_event import BaseEvent
from rabbitmq_sdk.event.impl.devices_manager.sensor_alarm import SensorAlarm

from app.models.notification import NotificationInputDto
from app.services.notification.notification_service import NotificationService


class SensorAlarmConsumer(BaseConsumer):
    def __init__(self, notification_service: NotificationService):
        super().__init__()
        self.notification_service = notification_service

    def get_event(self) -> Event:
        return Event.SENSOR_ALARM

    def event_class(self) -> Type[BaseEvent]:
        return SensorAlarm

    def do_handle(self, event):
        event: SensorAlarm = SensorAlarm.from_dict(event)
        self.notification_service.send_notification(
            NotificationInputDto(
                title="[ALARM TRIGGERED] Sensor: " + event.sensor_name,
                priority="5",
                message=f"Magnetic reed has been opened"
            )
        )