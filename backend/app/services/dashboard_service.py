from __future__ import annotations

import time
from functools import lru_cache
import json

import pandas as pd

from backend.app.config.settings import get_settings
from backend.app.ml.preprocessing import load_raw_datasets
from backend.app.services.training_service import load_metrics

_cache_timestamp = 0
_cached_stats = None


def dashboard_stats() -> dict:
    settings = get_settings()
    current_time = time.time()
    
    global _cache_timestamp, _cached_stats
    if _cached_stats is not None and (current_time - _cache_timestamp) < settings.cache_ttl_seconds:
        return _cached_stats

    summary_path = settings.data_processed_dir / "dashboard_summary.json"
    if summary_path.exists():
        result = json.loads(summary_path.read_text(encoding="utf-8"))
        result["metrics"] = load_metrics()
        _cached_stats = result
        _cache_timestamp = current_time
        return result
    
    processed = settings.data_processed_dir / "maintenance_features.csv"
    if processed.exists():
        df = pd.read_csv(processed, low_memory=False)
        sources = ["maintenance_features.csv"]
    else:
        bundle = load_raw_datasets(settings.data_raw_dir)
        df = bundle.frame
        sources = bundle.source_files

    metrics = load_metrics()
    if df.empty:
        result = demo_stats(metrics)
        _cached_stats = result
        _cache_timestamp = current_time
        return result

    numeric = df.select_dtypes(include="number")
    equipment_col = next((c for c in df.columns if "equipment" in c.lower() or "machine" in c.lower() or c.lower() == "id"), None)
    total_equipment = int(df[equipment_col].nunique()) if equipment_col else int(min(len(df), 250))
    failure_col = next((c for c in df.columns if c in {"failure_binary", "machine_failure", "target", "failure"}), None)
    if failure_col and pd.api.types.is_numeric_dtype(df[failure_col]):
        failed_rows = df[pd.to_numeric(df[failure_col], errors="coerce").fillna(0).astype(int) == 1]
        recent_failed_rows = failed_rows
        if "datetime" in df.columns:
            parsed_time = pd.to_datetime(df["datetime"], errors="coerce")
            max_time = parsed_time.max()
            if pd.notna(max_time):
                recent_mask = parsed_time >= max_time - pd.Timedelta(days=30)
                recent_failed_rows = failed_rows.loc[recent_mask.loc[failed_rows.index]]
        if equipment_col and equipment_col in df.columns:
            critical = int(recent_failed_rows[equipment_col].nunique())
        else:
            critical = int(recent_failed_rows.shape[0])
        event_rate = float(len(failed_rows) / max(len(df), 1))
    else:
        critical = max(1, total_equipment // 12)
        event_rate = critical / max(total_equipment, 1)

    result = {
        "sources": sources,
        "total_equipment": total_equipment,
        "critical_equipment": critical,
        "avg_failure_probability": round(min(0.95, event_rate), 3),
        "avg_rul": float(max(5, 100 * (1 - event_rate * 12))),
        "temperature": _mean_temperature(df, numeric),
        "vibration": _mean_for(numeric, "vib", 39.2),
        "pressure": _mean_for(numeric, "pressure", 94.7),
        "health_score": int(max(35, 95 - event_rate * 3000)),
        "metrics": metrics,
    }
    _cached_stats = result
    _cache_timestamp = current_time
    return result


def _mean_for(df: pd.DataFrame, hint: str, default: float) -> float:
    col = next((c for c in df.columns if hint in c.lower()), None)
    return float(round(df[col].mean(), 2)) if col else default


def _mean_temperature(full_df: pd.DataFrame, numeric: pd.DataFrame) -> float:
    kelvin_col = next((c for c in numeric.columns if "temperature" in c.lower() and "[k]" in c.lower()), None)
    if kelvin_col:
        return float(round(numeric[kelvin_col].mean() - 273.15, 2))
    return _mean_for(numeric, "temp", 67.4)


def demo_stats(metrics: dict) -> dict:
    return {
        "sources": [],
        "total_equipment": 128,
        "critical_equipment": 9,
        "avg_failure_probability": 0.18,
        "avg_rul": 64.5,
        "temperature": 68.2,
        "vibration": 41.8,
        "pressure": 96.1,
        "health_score": 84,
        "metrics": metrics,
    }
