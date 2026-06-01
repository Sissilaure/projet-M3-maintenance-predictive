from __future__ import annotations

import numpy as np
import pandas as pd


SENSOR_HINTS = ["temp", "temperature", "vibration", "pressure", "torque", "speed", "wear", "volt", "current", "rotational"]


def add_time_features(df: pd.DataFrame, time_col: str | None) -> pd.DataFrame:
    out = df.copy()
    if time_col and time_col in out.columns:
        if np.issubdtype(out[time_col].dtype, np.datetime64):
            out["hour"] = out[time_col].dt.hour
            out["dayofweek"] = out[time_col].dt.dayofweek
            out["month"] = out[time_col].dt.month
        else:
            out["cycle_index"] = pd.to_numeric(out[time_col], errors="coerce")
    return out


def sensor_columns(df: pd.DataFrame) -> list[str]:
    numeric = df.select_dtypes(include=["number"]).columns
    return [c for c in numeric if any(hint in c.lower() for hint in SENSOR_HINTS)]


def add_temporal_features(df: pd.DataFrame, equipment_col: str | None = None, time_col: str | None = None) -> pd.DataFrame:
    out = df.copy()
    sort_cols = [c for c in [equipment_col, time_col] if c and c in out.columns]
    if sort_cols:
        out = out.sort_values(sort_cols)

    sensors = sensor_columns(out)
    if not sensors:
        return out
    
    groups = out.groupby(equipment_col, dropna=False) if equipment_col and equipment_col in out.columns else [(None, out)]
    pieces = []
    for _, group in groups:
        group = group.copy()
        for col in sensors:
            series = group[col].astype(float)
            rolling_mean_3 = series.rolling(3, min_periods=1).mean()
            rolling_std_3 = series.rolling(3, min_periods=1).std().fillna(0)
            lag_1 = series.shift(1).bfill()
            trend_3 = series.diff().rolling(3, min_periods=1).mean().fillna(0)
            moving_avg_5 = series.rolling(5, min_periods=1).mean()
            rate_change = series.pct_change(fill_method=None).replace([np.inf, -np.inf], 0).fillna(0)
            
            group[f"{col}_rolling_mean_3"] = rolling_mean_3
            group[f"{col}_rolling_std_3"] = rolling_std_3
            group[f"{col}_lag_1"] = lag_1
            group[f"{col}_trend_3"] = trend_3
            group[f"{col}_moving_avg_5"] = moving_avg_5
            group[f"{col}_rate_change"] = rate_change
        pieces.append(group)
    return pd.concat(pieces, axis=0).sort_index()


def calculate_rul(df: pd.DataFrame, target_col: str | None, equipment_col: str | None, time_col: str | None) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    work = df.copy()
    if time_col and time_col in work.columns:
        work = work.sort_values([c for c in [equipment_col, time_col] if c and c in work.columns])
    if target_col and target_col in work.columns:
        failure = pd.to_numeric(work[target_col], errors="coerce").fillna(0).astype(int)
    else:
        failure = pd.Series(0, index=work.index)

    rul = pd.Series(index=work.index, dtype=float)
    group_iter = work.groupby(equipment_col, dropna=False) if equipment_col and equipment_col in work.columns else [(None, work)]
    for _, group in group_iter:
        idx = list(group.index)
        failure_positions = np.where(failure.loc[idx].to_numpy() == 1)[0]
        for pos, row_idx in enumerate(idx):
            future_failures = failure_positions[failure_positions >= pos]
            rul.loc[row_idx] = float(future_failures[0] - pos) if len(future_failures) else float(len(idx) - pos)
    return rul.fillna(rul.median() if rul.notna().any() else 0)
