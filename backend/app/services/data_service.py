"""Loads the processed CSV once and answers data questions with Pandas."""
import logging
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache

import pandas as pd

from app.core.config import (DATA_FILE, HEAVY_DAY_MM, LIVE_CACHE_MINUTES, LIVE_DATA,
                             RAINY_DAY_MM)
from app.services import live_service

log = logging.getLogger("rainsafe.data")
BASE_COLS = ["date", "rainfall_mm", "temperature_max_c", "temperature_min_c",
             "wind_speed_max_kmh"]


class DataUnavailable(Exception):
    pass


def _season(month):
    if month in (1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "pre_monsoon"
    if month in (6, 7, 8, 9):
        return "monsoon"
    return "post_monsoon"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling totals. A window needs ALL days present; missing is never 0."""
    df = df.sort_values("date").set_index("date")
    df = df.reindex(pd.date_range(df.index.min(), df.index.max(), freq="D"))
    df.index.name = "date"
    df["rain_3d_mm"] = df["rainfall_mm"].rolling(3, min_periods=3).sum()
    df["rain_7d_mm"] = df["rainfall_mm"].rolling(7, min_periods=7).sum()
    df["is_heavy_day"] = df["rainfall_mm"] >= HEAVY_DAY_MM
    df["season"] = df.index.month.map(_season)
    return df.reset_index()


@lru_cache(maxsize=1)
def load_base_df() -> pd.DataFrame:
    """The committed CSV (never changes while the server runs)."""
    if not DATA_FILE.exists():
        raise DataUnavailable(
            f"Data file missing: {DATA_FILE.name}. Run ml/build_features.py."
        )
    df = pd.read_csv(DATA_FILE, parse_dates=["date"])
    return df.sort_values("date").reset_index(drop=True)


_lock = threading.Lock()
_cache = {"df": None, "current": None, "ts": 0.0, "status": {}}


def _build_live(base: pd.DataFrame):
    frames, current = live_service.fetch_recent(base["date"].max(), live_service.today_ist())
    recent = pd.concat(frames).groupby("date", as_index=False).first()  # archive wins
    merged = pd.concat([base[BASE_COLS], recent[BASE_COLS]]).drop_duplicates("date", keep="first")
    return add_features(merged), current


def refresh():
    """Refresh the cache. Live data if possible, otherwise CSV (and say so)."""
    base = load_base_df()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    ttl = LIVE_CACHE_MINUTES * 60
    if not LIVE_DATA:
        df, current, mode, err = base, None, "csv_only", None
    else:
        try:
            df, current = _build_live(base)
            mode, err = "live", None
        except Exception as e:  # network down, API change, etc.
            log.warning("Live fetch failed: %s", e)
            err = f"{type(e).__name__}: {e}"
            if _cache["df"] is not None:  # keep last good live data
                df, current, mode = _cache["df"], _cache["current"], _cache["status"]["mode"]
            else:
                df, current, mode = base, None, "csv_fallback"
            ttl = 300  # retry sooner after a failure
    _cache.update(df=df, current=current, ts=time.time() - (LIVE_CACHE_MINUTES * 60 - ttl),
                  status={"mode": mode, "last_refreshed": now, "error": err,
                          "latest_complete_day": df["date"].max().strftime("%Y-%m-%d")})


def load_df() -> pd.DataFrame:
    with _lock:
        if _cache["df"] is None or time.time() - _cache["ts"] > LIVE_CACHE_MINUTES * 60:
            refresh()
        return _cache["df"]


def get_live() -> dict:
    load_df()
    return {"current": _cache["current"], "data_status": _cache["status"]}


def reset_cache():
    _cache.update(df=None, current=None, ts=0.0, status={})


def data_available() -> bool:
    return DATA_FILE.exists()


def warm_up():
    """Called in a background thread at startup so the first visitor is fast."""
    try:
        load_df()
    except Exception as e:
        log.warning("Warm-up failed: %s", e)


def num(v, digits=1):
    """NaN -> None so JSON shows null (never silently 0)."""
    return None if pd.isna(v) else round(float(v), digits)


def row_to_dict(row) -> dict:
    return {
        "date": row["date"].strftime("%Y-%m-%d"),
        "rainfall_mm": num(row["rainfall_mm"]),
        "temperature_max_c": num(row["temperature_max_c"]),
        "temperature_min_c": num(row["temperature_min_c"]),
        "wind_speed_max_kmh": num(row["wind_speed_max_kmh"]),
        "rain_3d_mm": num(row["rain_3d_mm"]),
        "rain_7d_mm": num(row["rain_7d_mm"]),
    }


def get_latest() -> dict:
    return row_to_dict(load_df().iloc[-1])


def get_row(date_str: str):
    df = load_df()
    match = df[df["date"] == pd.Timestamp(date_str)]
    return None if match.empty else match.iloc[0]


def filter_range(start=None, end=None) -> pd.DataFrame:
    df = load_df()
    if start:
        df = df[df["date"] >= pd.Timestamp(start)]
    if end:
        df = df[df["date"] <= pd.Timestamp(end)]
    return df


def get_summary() -> dict:
    df = load_df()
    rain = df["rainfall_mm"]
    peak = df.loc[rain.idxmax()]
    latest = df.iloc[-1]

    clim = df.groupby(df["date"].dt.month)["rainfall_mm"].mean()
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_avg = [
        {"month": months[m - 1], "avg_daily_mm": num(v, 2)} for m, v in clim.items()
    ]
    season = df.groupby("season")["rainfall_mm"].sum()
    years = len(df) / 365.25  # handles a partial current year
    seasonal = [
        {"season": s, "avg_total_mm_per_year": num(v / years)}
        for s, v in season.items()
    ]
    top = df.nlargest(5, "rain_3d_mm")
    return {
        "period": {
            "start": df["date"].min().strftime("%Y-%m-%d"),
            "end": df["date"].max().strftime("%Y-%m-%d"),
        },
        "average_daily_mm": num(rain.mean(), 2),
        "max_daily_mm": num(rain.max()),
        "max_daily_date": peak["date"].strftime("%Y-%m-%d"),
        "max_temperature_c": num(df["temperature_max_c"].max()),
        "min_temperature_c": num(df["temperature_min_c"].min()),
        "max_wind_kmh": num(df["wind_speed_max_kmh"].max()),
        "rainy_days": int((rain >= RAINY_DAY_MM).sum()),
        "heavy_days": int((rain >= HEAVY_DAY_MM).sum()),
        "rainy_day_threshold_mm": RAINY_DAY_MM,
        "heavy_day_threshold_mm": HEAVY_DAY_MM,
        "latest_date": latest["date"].strftime("%Y-%m-%d"),
        "data_status": _cache["status"],
        "latest_rain_3d_mm": num(latest["rain_3d_mm"]),
        "latest_rain_7d_mm": num(latest["rain_7d_mm"]),
        "monthly_average": monthly_avg,
        "seasonal": seasonal,
        "top_3day_events": [
            {"date": r["date"].strftime("%Y-%m-%d"), "rain_3d_mm": num(r["rain_3d_mm"])}
            for _, r in top.iterrows()
        ],
    }


def get_trends(granularity, start=None, end=None) -> list:
    df = filter_range(start, end)
    if df.empty:
        return []
    if granularity == "daily":
        return [
            {"period": r["date"].strftime("%Y-%m-%d"), "rainfall_mm": num(r["rainfall_mm"])}
            for _, r in df.iterrows()
        ]
    if granularity == "monthly":
        g = df.groupby(df["date"].dt.to_period("M"))["rainfall_mm"].sum(min_count=1)
        return [{"period": str(p), "rainfall_mm": num(v)} for p, v in g.items()]
    # annual
    out = []
    for year, part in df.groupby(df["date"].dt.year):
        r = part["rainfall_mm"]
        out.append({
            "period": str(year),
            "rainfall_mm": num(r.sum(min_count=1)),
            "heavy_days": int((r >= HEAVY_DAY_MM).sum()),
            "rainy_days": int((r >= RAINY_DAY_MM).sum()),
            "days_covered": int(len(part)),
            "partial_year": bool(len(part) < 365),
        })
    return out
