from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline

from backend.app.ml.evaluation import regression_metrics
from backend.app.ml.preprocessing import build_preprocessor

try:
    from xgboost import XGBRegressor
except Exception:  # pragma: no cover
    XGBRegressor = None


@dataclass
class RULTrainingResult:
    best_name: str
    best_pipeline: Pipeline
    metrics: dict[str, dict]


def candidate_regressors() -> dict:
    models = {
        "random_forest_regressor": RandomForestRegressor(n_estimators=160, random_state=42),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }
    if XGBRegressor is not None:
        models["xgboost_regressor"] = XGBRegressor(n_estimators=140, max_depth=4, learning_rate=0.08, random_state=42)
    return models


def train_rul_models(x: pd.DataFrame, y: pd.Series) -> RULTrainingResult:
    if len(x) < 8:
        raise ValueError("Le dataset RUL doit contenir suffisamment de lignes.")
    tscv = TimeSeriesSplit(n_splits=min(5, max(2, len(x) // 20)))
    metrics: dict[str, dict] = {}
    best_name = ""
    best_score = np.inf
    best_pipeline: Pipeline | None = None

    for name, model in candidate_regressors().items():
        fold_metrics = []
        for train_idx, test_idx in tscv.split(x):
            pipeline = Pipeline([("preprocess", build_preprocessor(x.iloc[train_idx])), ("model", clone(model))])
            pipeline.fit(x.iloc[train_idx], y.iloc[train_idx])
            pred = pipeline.predict(x.iloc[test_idx])
            fold_metrics.append(regression_metrics(y.iloc[test_idx], pred))
        avg = {k: float(sum(m[k] for m in fold_metrics) / len(fold_metrics)) for k in ["mae", "rmse", "r2"]}
        metrics[name] = avg
        if avg["rmse"] < best_score:
            best_name, best_score = name, avg["rmse"]
            best_pipeline = Pipeline([("preprocess", build_preprocessor(x)), ("model", clone(model))]).fit(x, y)

    assert best_pipeline is not None
    return RULTrainingResult(best_name, best_pipeline, metrics)


def save_rul_model(result: RULTrainingResult, path) -> None:
    joblib.dump({"name": result.best_name, "pipeline": result.best_pipeline, "metrics": result.metrics}, path)


def lstm_placeholder_note() -> str:
    return (
        "Un LSTM léger peut être entraîné lorsque les données contiennent des séquences longues par équipement. "
        "Le pipeline actuel privilégie les modèles tabulaires robustes pour garantir une démonstration fiable."
    )
