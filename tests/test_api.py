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
