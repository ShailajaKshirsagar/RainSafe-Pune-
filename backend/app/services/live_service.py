"""Fetches recent + current weather from Open-Meteo (free, no API key).

- Archive API  : verified daily data up to ~3 days ago
- Forecast API : past_days=7 fills the last few days; `current` = live conditions
"""
import logging

import pandas as pd
import requests

from app.core.config import (ARCHIVE_URL, FORECAST_URL, LATITUDE, LIVE_TIMEOUT_SECONDS,
                             LONGITUDE, TIMEZONE)

log = logging.getLogger("rainsafe.live")

DAILY_MAP = {
    "precipitation_sum": "rainfall_mm",
    "temperature_2m_max": "temperature_max_c",
    "temperature_2m_min": "temperature_min_c",
    "wind_speed_10m_max": "wind_speed_max_kmh",
}
CURRENT_VARS = ["temperature_2m", "relative_humidity_2m", "precipitation",
                "wind_speed_10m", "weather_code"]


def today_ist() -> pd.Timestamp:
    return pd.Timestamp.now(tz=TIMEZONE).normalize().tz_localize(None)


def _get(url, params):
    r = requests.get(url, params=params, timeout=LIVE_TIMEOUT_SECONDS)
    r.raise_for_status()
    return r.json()


def _daily_frame(payload) -> pd.DataFrame:
    d = payload["daily"]
    df = pd.DataFrame({"date": pd.to_datetime(d["time"])})
    for api_name, col in DAILY_MAP.items():
        df[col] = pd.to_numeric(pd.Series(d[api_name]), errors="coerce")
    df.loc[df["rainfall_mm"] < 0, "rainfall_mm"] = float("nan")  # invalid -> missing
    return df


def fetch_recent(base_end: pd.Timestamp, today: pd.Timestamp):
    """Return (daily_frames, current_dict) for days after base_end up to yesterday."""
    base = {"latitude": LATITUDE, "longitude": LONGITUDE, "timezone": TIMEZONE,
            "daily": ",".join(DAILY_MAP)}
    frames = []

    start, arch_end = base_end + pd.Timedelta(days=1), today - pd.Timedelta(days=3)
    if start <= arch_end:
        payload = _get(ARCHIVE_URL, {**base, "start_date": start.strftime("%Y-%m-%d"),
                                     "end_date": arch_end.strftime("%Y-%m-%d")})
        frames.append(_daily_frame(payload))

    fc = _get(FORECAST_URL, {**base, "past_days": 7, "forecast_days": 1,
                             "current": ",".join(CURRENT_VARS)})
    fdf = _daily_frame(fc)
    # keep only complete days (before today) that the CSV does not already have
    frames.append(fdf[(fdf["date"] < today) & (fdf["date"] > base_end)])

    cur = fc.get("current") or {}
    current = {
        "observed_at": cur.get("time"),
        "temperature_c": cur.get("temperature_2m"),
        "humidity_percent": cur.get("relative_humidity_2m"),
        "rain_mm_last_interval": cur.get("precipitation"),
        "wind_speed_kmh": cur.get("wind_speed_10m"),
        "weather_code": cur.get("weather_code"),
    } if cur else None
    return frames, current
