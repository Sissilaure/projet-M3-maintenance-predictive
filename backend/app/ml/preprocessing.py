from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class DatasetBundle:
    frame: pd.DataFrame
    source_files: list[str]
    target_column: str | None
    time_column: str | None
    equipment_column: str | None


FAILURE_CANDIDATES = [
    "failure_binary",
    "failure",
    "machine failure",
    "target",
    "fail",
    "breakdown",
    "failure_type",
    "failuretype",
]
TIME_CANDIDATES = ["datetime", "timestamp", "date", "time", "cycle", "cycle_id", "udi"]
EQUIPMENT_CANDIDATES = ["machineid", "machine_id", "equipment_id", "asset_id", "id", "product id", "productid"]


def _normalise_name(name: str) -> str:
    return name.strip().lower().replace("-", "_").replace(" ", "_")


def load_raw_datasets(raw_dir: Path) -> DatasetBundle:
    files = sorted([p for p in raw_dir.glob("*") if p.suffix.lower() in {".csv", ".xlsx", ".xls"}])
    file_map = {p.name.lower(): p for p in files}
    frames: list[pd.DataFrame] = []

    azure = _load_azure_predictive_maintenance(file_map)
    if azure is not None:
        frames.append(azure)

    ai4i_path = file_map.get("ai4i2020.csv")
    if ai4i_path is not None:
        frames.append(_load_ai4i(ai4i_path))

    consumed = {"pdm_telemetry.csv", "pdm_failures.csv", "pdm_errors.csv", "pdm_maint.csv", "pdm_machines.csv", "ai4i2020.csv"}
    for path in files:
        if path.name.lower() in consumed:
            continue
        df = _read_table(path)
        df["dataset_source"] = path.name
        if "failure_binary" not in df.columns:
            infer_failure_target(df)
        frames.append(df)

    if not frames:
        return DatasetBundle(pd.DataFrame(), [], None, None, None)

    frame = pd.concat(frames, ignore_index=True, sort=False)
    target = infer_failure_target(frame)
    time_col = infer_column(frame.columns, TIME_CANDIDATES)
    equipment_col = infer_column(frame.columns, EQUIPMENT_CANDIDATES)
    return DatasetBundle(frame, [p.name for p in files], target, time_col, equipment_col)


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 50:
            try:
                df = pd.read_csv(path, low_memory=False, dtype_backend="pyarrow")
            except (ImportError, ValueError):
                df = pd.read_csv(path, low_memory=False)
        else:
            df = pd.read_csv(path, low_memory=False)
    else:
        df = pd.read_excel(path)
    df.columns = [_normalise_name(c) for c in df.columns]
    return df


def _load_ai4i(path: Path) -> pd.DataFrame:
    df = _read_table(path)
    if "machine_failure" in df.columns:
        df["failure_binary"] = pd.to_numeric(df["machine_failure"], errors="coerce").fillna(0).astype(int)
    df["dataset_source"] = path.name
    df["equipment_id"] = df.get("product_id", pd.Series([None] * len(df))).astype(str)
    df["cycle"] = pd.to_numeric(df.get("udi"), errors="coerce")
    return df


def _load_azure_predictive_maintenance(file_map: dict[str, Path]) -> pd.DataFrame | None:
    telemetry_path = file_map.get("pdm_telemetry.csv")
    if telemetry_path is None:
        return None

    telemetry = _read_table(telemetry_path)
    telemetry["datetime"] = pd.to_datetime(telemetry["datetime"], errors="coerce")
    telemetry["dataset_source"] = "Azure Predictive Maintenance"

    machines_path = file_map.get("pdm_machines.csv")
    if machines_path is not None:
        machines = _read_table(machines_path)
        telemetry = telemetry.merge(machines, on="machineid", how="left")

    failures_path = file_map.get("pdm_failures.csv")
    if failures_path is not None:
        failures = _read_table(failures_path)
        failures["datetime"] = pd.to_datetime(failures["datetime"], errors="coerce")
        failures["failure_binary"] = 1
        failures["failure_component"] = failures["failure"]
        telemetry = telemetry.merge(
            failures[["datetime", "machineid", "failure_binary", "failure_component"]],
            on=["datetime", "machineid"],
            how="left",
        )
    else:
        telemetry["failure_binary"] = 0
    telemetry["failure_binary"] = telemetry["failure_binary"].fillna(0).astype(int)
    telemetry["failure_component"] = telemetry.get("failure_component", pd.Series(index=telemetry.index, dtype="object")).fillna("no_failure")

    errors_path = file_map.get("pdm_errors.csv")
    if errors_path is not None:
        errors = _read_table(errors_path)
        errors["datetime"] = pd.to_datetime(errors["datetime"], errors="coerce")
        error_counts = (
            pd.get_dummies(errors, columns=["errorid"], prefix="error")
            .groupby(["datetime", "machineid"], as_index=False)
            .sum(numeric_only=True)
        )
        telemetry = telemetry.merge(error_counts, on=["datetime", "machineid"], how="left")

    maint_path = file_map.get("pdm_maint.csv")
    if maint_path is not None:
        maint = _read_table(maint_path)
        maint["datetime"] = pd.to_datetime(maint["datetime"], errors="coerce")
        maint_counts = (
            pd.get_dummies(maint, columns=["comp"], prefix="maint")
            .groupby(["datetime", "machineid"], as_index=False)
            .sum(numeric_only=True)
        )
        telemetry = telemetry.merge(maint_counts, on=["datetime", "machineid"], how="left")

    count_cols = [c for c in telemetry.columns if c.startswith("error_") or c.startswith("maint_")]
    telemetry[count_cols] = telemetry[count_cols].fillna(0).astype(int)
    return telemetry


def infer_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    normalised = {_normalise_name(c): c for c in columns}
    for candidate in candidates:
        key = _normalise_name(candidate)
        if key in normalised:
            return normalised[key]
    for col in columns:
        low = col.lower()
        if any(_normalise_name(candidate) in low for candidate in candidates):
            return col
    return None


def infer_failure_target(df: pd.DataFrame) -> str | None:
    col = infer_column(df.columns, FAILURE_CANDIDATES)
    if col is None:
        return None
    if df[col].dtype == "object":
        lowered = df[col].astype(str).str.lower()
        if lowered.isin(["no failure", "none", "normal", "0"]).any():
            df["failure_binary"] = (~lowered.isin(["no failure", "none", "normal", "0", "nan"])).astype(int)
        else:
            df["failure_binary"] = lowered.ne("0").astype(int)
        return "failure_binary"
    return col


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    for col in cleaned.columns:
        if cleaned[col].dtype == "object" and any(token in col.lower() for token in ["date", "time"]):
            parsed = pd.to_datetime(cleaned[col], errors="coerce")
            if parsed.notna().mean() > 0.75:
                cleaned[col] = parsed
    cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
    return cleaned.drop_duplicates()


def split_features_target(df: pd.DataFrame, target: str) -> tuple[pd.DataFrame, pd.Series]:
    y = df[target].fillna(0).astype(int)
    leakage_cols = {
        target,
        "failure_binary",
        "machine_failure",
        "failure",
        "failure_component",
        "twf",
        "hdf",
        "pwf",
        "osf",
        "rnf",
    }
    high_cardinality_ids = {"product_id", "equipment_id"}
    drop_cols = leakage_cols | high_cardinality_ids
    x = df.drop(columns=[c for c in drop_cols if c in df.columns])
    return x, y


def build_preprocessor(x: pd.DataFrame) -> ColumnTransformer:
    usable = x.dropna(axis=1, how="all")
    numeric_features = usable.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = usable.select_dtypes(include=["object", "category"]).columns.tolist()
    datetime_features = x.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()

    transformers = []
    if numeric_features:
        transformers.append(("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features))
    if categorical_features:
        transformers.append(("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical_features))
    if datetime_features:
        # Datetime values are expanded in feature_engineering; remaining datetime columns are dropped.
        transformers.append(("drop_datetime", "drop", datetime_features))
    return ColumnTransformer(transformers=transformers, remainder="drop")
