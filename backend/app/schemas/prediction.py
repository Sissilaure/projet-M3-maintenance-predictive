from typing import Any

from pydantic import BaseModel, Field


class EquipmentReading(BaseModel):
    equipment_id: str = Field(default="EQ-001")
    timestamp: str | None = None
    values: dict[str, Any] = Field(default_factory=dict)


class FailurePrediction(BaseModel):
    equipment_id: str
    failure_probability: float
    predicted_failure: bool
    prediction_horizon: str = "24h"
    risk_level: str
    top_factors: list[dict[str, float | str]]


class RULPrediction(BaseModel):
    equipment_id: str
    rul: float
    unit: str = "cycles_or_hours"
    confidence: str


class Alert(BaseModel):
    equipment_id: str
    level: str
    title: str
    message: str
    recommendation: str
    score: float
