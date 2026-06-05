from __future__ import annotations

from dataclasses import dataclass

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from backend.app.ml.evaluation import classification_metrics
from backend.app.ml.preprocessing import build_preprocessor

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover
    XGBClassifier = None

try:
    from lightgbm import LGBMClassifier
except Exception:  # pragma: no cover
    LGBMClassifier = None


@dataclass
class TrainingResult:
    best_name: str
    best_pipeline: Pipeline
    metrics: dict[str, dict]
    prediction_horizon: str


def candidate_models(y: pd.Series | None = None) -> dict:
    scale_pos_weight = 1.0
    if y is not None:
        positives = max(int(y.sum()), 1)
        negatives = max(int(len(y) - positives), 1)
        scale_pos_weight = negatives / positives
    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=160, random_state=42, class_weight="balanced"),
        "svm": SVC(probability=True, class_weight="balanced", random_state=42),
    }
    if XGBClassifier is not None:
        models["xgboost"] = XGBClassifier(
            n_estimators=180,
            max_depth=4,
            learning_rate=0.06,
            subsample=0.9,
            colsample_bytree=0.9,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=42,
        )
    if LGBMClassifier is not None:
        models["lightgbm"] = LGBMClassifier(
            n_estimators=180,
            learning_rate=0.06,
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        )
    return models


def train_classifiers(x: pd.DataFrame, y: pd.Series) -> TrainingResult:
    if len(x) < 8 or y.nunique() < 2:
        raise ValueError("Le dataset doit contenir au moins deux classes et suffisamment de lignes.")

    tscv = TimeSeriesSplit(n_splits=min(5, max(2, len(x) // 20)))
    metrics: dict[str, dict] = {}
    best_name = ""
    best_score = -1.0
    best_pipeline: Pipeline | None = None

    for name, model in candidate_models(y).items():
        fold_metrics = []
        for train_idx, test_idx in tscv.split(x):
            pipeline = Pipeline([("preprocess", build_preprocessor(x.iloc[train_idx])), ("model", clone(model))])
            pipeline.fit(x.iloc[train_idx], y.iloc[train_idx])
            pred = pipeline.predict(x.iloc[test_idx])
            proba = pipeline.predict_proba(x.iloc[test_idx])[:, 1] if hasattr(pipeline, "predict_proba") else None
            fold_metrics.append(classification_metrics(y.iloc[test_idx], pred, proba))
        avg = {k: float(sum(m[k] for m in fold_metrics) / len(fold_metrics)) for k in ["accuracy", "precision", "recall", "f1", "roc_auc"]}
        avg["confusion_matrix"] = fold_metrics[-1]["confusion_matrix"]
        metrics[name] = avg
        score = avg["f1"]
        if score > best_score:
            best_name, best_score = name, score
            best_pipeline = Pipeline([("preprocess", build_preprocessor(x)), ("model", clone(model))]).fit(x, y)

    assert best_pipeline is not None
    return TrainingResult(best_name, best_pipeline, metrics, prediction_horizon="24h")


def save_classifier(result: TrainingResult, path) -> None:
    joblib.dump(
        {
            "name": result.best_name,
            "pipeline": result.best_pipeline,
            "metrics": result.metrics,
            "prediction_horizon": result.prediction_horizon,
        },
        path,
    )
