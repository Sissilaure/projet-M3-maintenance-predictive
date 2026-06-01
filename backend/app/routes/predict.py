from fastapi import APIRouter, Request
from backend.app.core.limiter import limiter

from backend.app.ml.inference import predict_failure, predict_rul
from backend.app.schemas.prediction import EquipmentReading, FailurePrediction, RULPrediction

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("/failure", response_model=FailurePrediction)
@limiter.limit("100/minute")
async def failure_prediction(request: Request, reading: EquipmentReading):
    return predict_failure(reading.equipment_id, reading.values)


@router.post("/rul", response_model=RULPrediction)
@limiter.limit("100/minute")
async def rul_prediction(request: Request, reading: EquipmentReading):
    return predict_rul(reading.equipment_id, reading.values)