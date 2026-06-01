from __future__ import annotations

import numpy as np
import pandas as pd


def top_feature_factors(pipeline, x: pd.DataFrame, limit: int = 8) -> list[dict[str, float | str]]:
    model = pipeline.named_steps.get("model") if hasattr(pipeline, "named_steps") else None
    preprocess = pipeline.named_steps.get("preprocess") if hasattr(pipeline, "named_steps") else None
    if model is None:
        return []
    try:
        names = preprocess.get_feature_names_out() if preprocess is not None else x.columns
    except Exception:
        names = np.array(x.columns)
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = np.abs(model.coef_).ravel()
    else:
        return []
    order = np.argsort(values)[::-1][:limit]
    return [{"feature": str(names[i]).split("__")[-1], "importance": float(values[i])} for i in order if i < len(names)]


def shap_summary_payload(pipeline, x: pd.DataFrame, sample_size: int = 50) -> dict:
    try:
        import shap

        sample = x.tail(sample_size)
        transformed = pipeline.named_steps["preprocess"].transform(sample)
        model = pipeline.named_steps["model"]
        explainer = shap.Explainer(model)
        values = explainer(transformed)
        means = np.abs(values.values).mean(axis=0)
        names = pipeline.named_steps["preprocess"].get_feature_names_out()
        order = np.argsort(means)[::-1][:12]
        return {"features": [str(names[i]).split("__")[-1] for i in order], "mean_abs_shap": [float(means[i]) for i in order]}
    except Exception as exc:
        return {"features": [], "mean_abs_shap": [], "note": f"SHAP indisponible pour ce modèle ou ce contexte: {exc}"}
