import pandas as pd

from backend.app.ml.feature_engineering import add_temporal_features, calculate_rul


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
