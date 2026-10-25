from fastapi.testclient import TestClient

from app.main import app
from app.services import risk_service

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["data_file_available"] is True


def test_current_is_not_live():
    d = client.get("/api/weather/current").json()
    assert d["is_live"] is False and d["data_type"] == "daily_observation"


def test_history_filter():
    d = client.get("/api/weather/history?start=2024-07-01&end=2024-07-31").json()
    assert d["count"] == 31


def test_summary():
    d = client.get("/api/rainfall/summary").json()
    assert d["max_daily_mm"] == 74.2 and d["heavy_days"] == 3
    assert len(d["monthly_average"]) == 12


def test_trends():
    for g, n in [("annual", 6), ("monthly", 72)]:
        assert len(client.get(f"/api/rainfall/trends?granularity={g}").json()["points"]) == n
    assert client.get("/api/rainfall/trends?granularity=bad").status_code == 422


def test_risk_default_and_high_day():
    assert client.get("/api/risk/assessment").json()["category"] == "low"
    d = client.get("/api/risk/assessment?date=2025-05-26").json()
    assert d["category"] == "high" and d["triggered_rules"]


def test_risk_invalid_inputs():
    assert client.get("/api/risk/assessment?date=abc").status_code == 422
    assert client.get("/api/risk/assessment?date=2030-01-01").status_code == 404


def test_areas():
    assert len(client.get("/api/areas").json()) >= 5
    assert client.get("/api/areas/nowhere").status_code == 404
    assert client.get("/api/areas/kothrud").status_code == 200


def test_cors_header():
    r = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"


# ---- risk rule unit tests ----
def test_boundaries():
    assert risk_service.assess(64.5, 0, 0)["category"] == "high"
    assert risk_service.assess(64.4, 0, 0)["category"] == "moderate"
    assert risk_service.assess(34.9, 59.9, 99.9)["category"] == "low"
    assert risk_service.assess(0, 100, 0)["category"] == "high"


def test_missing_not_zero():
    assert risk_service.assess(None, None, None)["category"] == "unknown"
    r = risk_service.assess(None, None, 150)
    assert r["category"] == "high" and "rain_1d_mm" in r["missing_measurements"]


def test_deterministic():
    assert risk_service.assess(40, 70, 90) == risk_service.assess(40, 70, 90)
