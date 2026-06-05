from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_failure_prediction_heuristic():
    response = client.post(
        "/predict/failure",
        json={"equipment_id": "TRUCK-001", "values": {"temperature": 95, "vibration": 66, "pressure": 130}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["failure_probability"] > 0.5
    assert payload["risk_level"] in {"moyen", "critique"}


def test_rul_prediction_heuristic():
    response = client.post(
        "/predict/rul",
        json={"equipment_id": "TRUCK-002", "values": {"temperature": 95, "vibration": 66, "pressure": 130}},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["rul"] >= 0
    assert payload["confidence"] in {"haute", "moyenne", "critique"}


def test_metrics_route_returns_object():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_dashboard_stats_route_returns_summary():
    response = client.get("/dashboard/stats")
    assert response.status_code == 200
    summary = response.json()
    assert "total_equipment" in summary
    assert "avg_failure_probability" in summary
    assert "metrics" in summary
