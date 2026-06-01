from fastapi import APIRouter

from backend.app.ml.inference import alerts_for_reading
from backend.app.schemas.prediction import Alert, EquipmentReading

router = APIRouter(tags=["alerts"])


@router.post("/alerts", response_model=list[Alert])
async def alerts(reading: EquipmentReading):
    return alerts_for_reading(reading.equipment_id, reading.values)


@router.get("/alerts", response_model=list[Alert])
async def sample_alerts():
    reading = EquipmentReading(
        equipment_id="TRUCK-042",
        values={"temperature": 91, "vibration": 62, "pressure": 131, "tool_wear": 210},
    )
    return alerts_for_reading(reading.equipment_id, reading.values)