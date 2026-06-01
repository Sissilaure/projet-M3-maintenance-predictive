from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import warnings

import joblib
import pandas as pd

from backend.app.config.settings import get_settings
from backend.app.ml.alerts import generate_alerts, risk_level
from backend.app.ml.explainability import top_feature_factors
from backend.app.schemas.prediction import FailurePrediction, RULPrediction


CLASSIFIER_FILE = "classifier.joblib"
RUL_FILE = "rul_model.joblib"


@lru_cache(maxsize=2)
def _load_artifact(filename: str):
    path = get_settings().model_dir / filename
    if not path.exists():
        return None
    return joblib.load(path)


def predict_failure(equipment_id: str, values: dict) -> FailurePrediction:
    artifact = _load_artifact(CLASSIFIER_FILE)
    frame = pd.DataFrame([values])
    if artifact is None:
        probability = heuristic_failure_probability(values)
        factors = [{"feature": "heuristique_temperature_vibration_pression", "importance": probability}]
    else:
        pipeline = artifact["pipeline"]
        frame = _align_to_training_columns(frame, pipeline)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
            model_probability = float(pipeline.predict_proba(frame)[0, 1]) if hasattr(pipeline, "predict_proba") else float(pipeline.predict(frame)[0])
        probability = max(model_probability, heuristic_failure_probability(values))
        factors = top_feature_factors(pipeline, frame)
    return FailurePrediction(
        equipment_id=equipment_id,
        failure_probability=probability,
        predicted_failure=probability >= 0.5,
        risk_level=risk_level(probability),
        top_factors=factors,
    )


def predict_rul(equipment_id: str, values: dict) -> RULPrediction:
    artifact = _load_artifact(RUL_FILE)
    if artifact is None:
        rul = heuristic_rul(values)
    else:
        frame = _align_to_training_columns(pd.DataFrame([values]), artifact["pipeline"])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names.*")
            rul = float(artifact["pipeline"].predict(frame)[0])
    confidence = "haute" if rul > 30 else "moyenne" if rul > 10 else "critique"
    return RULPrediction(equipment_id=equipment_id, rul=max(0.0, rul), confidence=confidence)


def heuristic_failure_probability(values: dict) -> float:
    text = {str(k).lower(): v for k, v in values.items()}
    score = 0.15
    for key, val in text.items():
        try:
            num = float(val)
        except (TypeError, ValueError):
            continue
        if "temp" in key:
            score += max(0, (num - 60) / 80)
        if "vib" in key:
            score += max(0, (num - 35) / 70)
        if "pressure" in key or "pression" in key:
            score += max(0, (num - 90) / 120)
        if "wear" in key:
            score += max(0, num / 300)
    return float(min(0.98, score))


def heuristic_rul(values: dict) -> float:
    probability = heuristic_failure_probability(values)
    return float(max(3, 100 * (1 - probability)))


def alerts_for_reading(equipment_id: str, values: dict):
    failure = predict_failure(equipment_id, values)
    rul = predict_rul(equipment_id, values)
    return generate_alerts(equipment_id, values, failure.failure_probability, rul.rul)


def _align_to_training_columns(frame: pd.DataFrame, pipeline) -> pd.DataFrame:
    preprocess = pipeline.named_steps.get("preprocess") if hasattr(pipeline, "named_steps") else None
    columns = getattr(preprocess, "feature_names_in_", None)
    if columns is None:
        return frame
    aligned = frame.copy()
    for col in columns:
        if col not in aligned.columns:
            aligned[col] = None
    return aligned[list(columns)]
