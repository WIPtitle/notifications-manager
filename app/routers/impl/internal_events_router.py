import os
import uuid
from datetime import datetime, timezone

from fastapi import Response, UploadFile, File, Form
from pydantic import BaseModel

from app.config.bindings import inject
from app.models.notification import NotificationInputDto
from app.routers.router_wrapper import RouterWrapper
from app.services.notification.notification_service import NotificationService

SNAPSHOTS_DIR = "/var/lib/notifications-manager/data/snapshots"


class SensorAlarmRequest(BaseModel):
    sensor_name: str


class InternalEventsRouter(RouterWrapper):
    @inject
    def __init__(self, notification_service: NotificationService):
        super().__init__(prefix="/internal/alarm")
        self.notification_service = notification_service
        os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

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

        @self.router.post("/motion-warning")
        async def on_motion_warning(
            camera_name: str = Form(...),
            snapshot: UploadFile | None = File(None),
        ):
            snapshot_filename = None
            if snapshot and snapshot.size and snapshot.size > 0:
                ext = "jpg"
                ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
                snapshot_filename = f"{ts}_{uuid.uuid4().hex[:8]}.{ext}"
                filepath = os.path.join(SNAPSHOTS_DIR, snapshot_filename)
                content = await snapshot.read()
                with open(filepath, "wb") as f:
                    f.write(content)

            self.notification_service.send_notification(
                NotificationInputDto(
                    title="MOTION WARNING",
                    priority="3",
                    message=f"Motion detected on camera {camera_name}.",
                ),
                snapshot_filename=snapshot_filename,
            )
            return Response(status_code=204)
