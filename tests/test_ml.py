import pandas as pd

from backend.app.ml.feature_engineering import add_temporal_features, calculate_rul
from backend.app.ml.preprocessing import derive_predictive_failure_target, split_features_target


def test_temporal_features_are_created():
    df = pd.DataFrame({
        "equipment_id": ["A", "A", "A"],
        "cycle": [1, 2, 3],
        "temperature": [60, 70, 90],
        "vibration": [20, 30, 50],
    })
    out = add_temporal_features(df, "equipment_id", "cycle")
    assert "temperature_rolling_mean_3" in out.columns
    assert "vibration_rate_change" in out.columns


def test_rul_calculation():
    df = pd.DataFrame({"equipment_id": ["A", "A", "A", "A"], "cycle": [1, 2, 3, 4], "failure": [0, 0, 1, 0]})
    rul = calculate_rul(df, "failure", "equipment_id", "cycle")
    assert list(rul.iloc[:3]) == [2.0, 1.0, 0.0]


def test_derive_predictive_failure_target_by_steps():
    df = pd.DataFrame({
        "equipment_id": ["A", "A", "A", "A"],
        "cycle": [1, 2, 3, 4],
        "failure": [0, 1, 0, 0],
    })
    out, label = derive_predictive_failure_target(df, "failure", "equipment_id", "cycle", horizon_steps=2)
    assert label == "failure_in_next_2_steps"
    assert out[label].tolist() == [1, 0, 0, 0]


def test_derive_predictive_failure_target_by_hours():
    df = pd.DataFrame({
        "equipment_id": ["A", "A", "A"],
        "datetime": pd.to_datetime(["2024-01-01 00:00", "2024-01-01 12:00", "2024-01-02 00:00"]),
        "failure": [0, 0, 1],
    })
    out, label = derive_predictive_failure_target(df, "failure", "equipment_id", "datetime", horizon_hours=24)
    assert label == "failure_in_next_24h"
    assert out[label].tolist() == [1, 1, 0]


def test_split_features_target_drops_leakage_columns():
    df = pd.DataFrame({
        "equipment_id": ["A", "B"],
        "failure": [0, 1],
        "temperature": [60, 70],
        "failure_binary": [0, 1],
    })
    x, y = split_features_target(df, "failure")
    assert "failure" not in x.columns
    assert "failure_binary" not in x.columns
    assert y.tolist() == [0, 1]
