from fastapi import Response
from pydantic import BaseModel

from app.config.bindings import inject
from app.models.notification import NotificationInputDto
from app.routers.router_wrapper import RouterWrapper
from app.services.notification.notification_service import NotificationService


class SensorAlarmRequest(BaseModel):
    sensor_name: str


class InternalEventsRouter(RouterWrapper):
    @inject
    def __init__(self, notification_service: NotificationService):
        super().__init__(prefix="/internal/alarm")
        self.notification_service = notification_service

    def _define_routes(self):
        @self.router.post("/sensor-alarm")
        def on_sensor_alarm(request: SensorAlarmRequest):
            self.notification_service.send_notification(
                NotificationInputDto(
                    title="ALARM TRIGGERED",
                    priority="5",
                    message=f"Sensor {request.sensor_name} has been triggered.",
                )
            )
            return Response(status_code=204)
