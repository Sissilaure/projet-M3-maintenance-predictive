from __future__ import annotations

import json
import pandas as pd

from backend.app.config.settings import get_settings
from backend.app.ml.classification import save_classifier, train_classifiers
from backend.app.ml.feature_engineering import add_temporal_features, add_time_features, calculate_rul
from backend.app.ml.preprocessing import clean_dataframe, load_raw_datasets, split_features_target
from backend.app.ml.rul_model import save_rul_model, train_rul_models


def train_all() -> dict:
    settings = get_settings()
    bundle = load_raw_datasets(settings.data_raw_dir)
    if bundle.frame.empty:
        raise ValueError("Aucun dataset CSV/XLSX trouvé dans data/raw. Placez les datasets fournis dans ce dossier.")

    df = clean_dataframe(bundle.frame)
    df = add_time_features(df, bundle.time_column)
    df = add_temporal_features(df, bundle.equipment_column, bundle.time_column)
    processed_path = settings.data_processed_dir / "maintenance_features.csv"
    df.to_csv(processed_path, index=False)
    train_df = select_training_rows(df, settings.training_max_rows, bundle.time_column)

    response: dict = {
        "sources": bundle.source_files,
        "rows": int(len(df)),
        "training_rows": int(len(train_df)),
        "columns": int(len(df.columns)),
        "target_column": bundle.target_column,
        "time_column": bundle.time_column,
        "equipment_column": bundle.equipment_column,
        "processed_path": str(processed_path),
    }

    if bundle.target_column:
        x, y = split_features_target(train_df, bundle.target_column)
        classifier = train_classifiers(x, y)
        save_classifier(classifier, settings.model_dir / "classifier.joblib")
        response["classification"] = {"best_model": classifier.best_name, "metrics": classifier.metrics}

        rul = calculate_rul(train_df, bundle.target_column, bundle.equipment_column, bundle.time_column)
        x_rul = x.copy()
        rul_result = train_rul_models(x_rul, rul)
        save_rul_model(rul_result, settings.model_dir / "rul_model.joblib")
        response["rul"] = {"best_model": rul_result.best_name, "metrics": rul_result.metrics}
    else:
        response["warning"] = "Aucune colonne cible de panne détectée automatiquement."

    metrics_path = settings.model_dir / "metrics.json"
    metrics_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    summary = build_dashboard_summary(df, response, bundle.equipment_column, bundle.time_column)
    (settings.data_processed_dir / "dashboard_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return response


def load_metrics() -> dict:
    path = get_settings().model_dir / "metrics.json"
    if not path.exists():
        return {
            "status": "not_trained",
            "message": "Lancez POST /train après avoir placé les datasets dans data/raw.",
        }
    return json.loads(path.read_text(encoding="utf-8"))


def select_training_rows(df: pd.DataFrame, max_rows: int, time_column: str | None = None) -> pd.DataFrame:
    """Keep training fast while preserving both datasets and chronological order."""
    if len(df) <= max_rows:
        return df.reset_index(drop=True)

    if "dataset_source" not in df.columns:
        return _sort_for_time(df, time_column).tail(max_rows).reset_index(drop=True)

    sources = [source for source in df["dataset_source"].dropna().unique().tolist()]
    rows_per_source = max(1, max_rows // max(len(sources), 1))
    parts = []
    for source in sources:
        source_df = _sort_for_time(df[df["dataset_source"].eq(source)], time_column)
        positives = source_df[source_df.get("failure_binary", 0).eq(1)] if "failure_binary" in source_df.columns else source_df.iloc[0:0]
        tail = source_df.tail(rows_per_source)
        part = pd.concat([tail, positives.tail(min(len(positives), rows_per_source // 5))], ignore_index=False)
        parts.append(part.drop_duplicates())
    sampled = pd.concat(parts, ignore_index=False).drop_duplicates()
    return _sort_for_time(sampled, time_column).tail(max_rows).reset_index(drop=True)


def _sort_for_time(df: pd.DataFrame, time_column: str | None) -> pd.DataFrame:
    sort_cols = []
    if "dataset_source" in df.columns:
        sort_cols.append("dataset_source")
    if time_column and time_column in df.columns:
        sort_cols.append(time_column)
    elif "cycle" in df.columns:
        sort_cols.append("cycle")
    if sort_cols:
        return df.sort_values(sort_cols)
    return df


def build_dashboard_summary(df: pd.DataFrame, metrics: dict, equipment_col: str | None, time_col: str | None) -> dict:
    failure = pd.to_numeric(df.get("failure_binary", pd.Series(0, index=df.index)), errors="coerce").fillna(0).astype(int)
    total_equipment = int(df[equipment_col].nunique()) if equipment_col and equipment_col in df.columns else int(min(len(df), 250))
    failed_rows = df[failure.eq(1)]
    recent_failed_rows = failed_rows
    if time_col and time_col in df.columns:
        parsed = pd.to_datetime(df[time_col], errors="coerce")
        max_time = parsed.max()
        if pd.notna(max_time):
            recent_failed_rows = failed_rows.loc[parsed.loc[failed_rows.index] >= max_time - pd.Timedelta(days=30)]
    critical = int(recent_failed_rows[equipment_col].nunique()) if equipment_col and equipment_col in df.columns else int(len(recent_failed_rows))
    event_rate = float(failure.mean())
    numeric = df.select_dtypes(include="number")
    return {
        "sources": metrics.get("sources", []),
        "total_equipment": total_equipment,
        "critical_equipment": critical,
        "avg_failure_probability": round(min(0.95, event_rate), 4),
        "avg_rul": float(round(max(5, 100 * (1 - event_rate * 12)), 2)),
        "temperature": _summary_temperature(numeric),
        "vibration": _summary_mean(numeric, "vib", 39.2),
        "pressure": _summary_mean(numeric, "pressure", 94.7),
        "health_score": int(max(35, 95 - event_rate * 3000)),
        "metrics": metrics,
    }


def _summary_mean(df: pd.DataFrame, hint: str, default: float) -> float:
    col = next((c for c in df.columns if hint in c.lower()), None)
    return float(round(df[col].mean(), 2)) if col else default


def _summary_temperature(df: pd.DataFrame) -> float:
    kelvin_col = next((c for c in df.columns if "temperature" in c.lower() and "[k]" in c.lower()), None)
    if kelvin_col:
        return float(round(df[kelvin_col].mean() - 273.15, 2))
    return _summary_mean(df, "temp", 67.4)
