"""Tests the live-data merge using FAKE Open-Meteo responses (no internet)."""
import pandas as pd

from app.services import data_service, live_service


def _fake_daily(start, end, rain):
    days = pd.date_range(start, end)
    return {"daily": {
        "time": [d.strftime("%Y-%m-%d") for d in days],
        "precipitation_sum": [rain] * len(days),
        "temperature_2m_max": [30.0] * len(days),
        "temperature_2m_min": [20.0] * len(days),
        "wind_speed_10m_max": [10.0] * len(days),
    }}


def test_live_merge(monkeypatch):
    today = pd.Timestamp("2026-03-10")
    monkeypatch.setattr(live_service, "today_ist", lambda: today)
    monkeypatch.setattr(data_service, "LIVE_DATA", True)

    def fake_get(url, params):
        if "archive" in url:  # 2026-01-01 .. 2026-03-07
            return _fake_daily(params["start_date"], params["end_date"], 1.0)
        payload = _fake_daily("2026-03-03", "2026-03-10", 50.0)  # past 7 days + today
        payload["current"] = {"time": "2026-03-10T14:00", "temperature_2m": 31.5,
                              "relative_humidity_2m": 40, "precipitation": 0.0,
                              "wind_speed_10m": 12.0, "weather_code": 1}
        return payload

    monkeypatch.setattr(live_service, "_get", fake_get)
    data_service.reset_cache()
    df = data_service.load_df()

    assert df["date"].max() == pd.Timestamp("2026-03-09")      # yesterday, not today
    assert df["date"].is_unique and df["date"].is_monotonic_increasing
    assert len(df) == 2192 + 31 + 28 + 9                         # no gaps, no duplicates
    # archive wins on overlap (1.0, not 50.0); forecast fills the last days
    assert df.loc[df["date"] == "2026-03-05", "rainfall_mm"].iloc[0] == 1.0
    assert df.loc[df["date"] == "2026-03-09", "rainfall_mm"].iloc[0] == 50.0
    assert df.iloc[-1]["rain_3d_mm"] == 101.0   # 1 + 50 + 50
    live = data_service.get_live()
    assert live["data_status"]["mode"] == "live"
    assert live["current"]["temperature_c"] == 31.5
    data_service.reset_cache()


def test_fallback_when_offline(monkeypatch):
    monkeypatch.setattr(data_service, "LIVE_DATA", True)

    def boom(url, params):
        raise ConnectionError("no internet")

    monkeypatch.setattr(live_service, "_get", boom)
    data_service.reset_cache()
    df = data_service.load_df()
    assert df["date"].max() == pd.Timestamp("2025-12-31")        # CSV used
    status = data_service.get_live()["data_status"]
    assert status["mode"] == "csv_fallback" and "no internet" in status["error"]
    data_service.reset_cache()
