import re
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.config import DATA_SOURCE, LOCATION_NAME
from app.schemas.schemas import Area, Observation, RiskAssessment
from app.services import advisory_service, area_service, data_service, risk_service

router = APIRouter(prefix="/api")
DATE_RE = r"^\d{4}-\d{2}-\d{2}$"


def _check_date(value: Optional[str], name: str):
    if value is None:
        return
    if not re.match(DATE_RE, value):
        raise HTTPException(422, f"{name} must be in YYYY-MM-DD format")
    try:
        import pandas as pd
        pd.Timestamp(value)
    except ValueError:
        raise HTTPException(422, f"{name} is not a valid date")


@router.get("/weather/current", response_model=Observation)
def current_weather():
    return {**data_service.get_latest(), "source": DATA_SOURCE, "location": LOCATION_NAME}


@router.get("/weather/live")
def live_weather():
    """Current conditions (Open-Meteo model) + how fresh the dataset is."""
    info = data_service.get_live()
    return {
        "is_live": info["current"] is not None,
        "current": info["current"],
        "data_status": info["data_status"],
        "source": "Open-Meteo Forecast API (model-based current conditions)",
        "location": LOCATION_NAME,
    }


@router.get("/weather/history")
def weather_history(start: Optional[str] = None, end: Optional[str] = None):
    _check_date(start, "start")
    _check_date(end, "end")
    df = data_service.filter_range(start, end)
    return {
        "count": len(df),
        "source": DATA_SOURCE,
        "location": LOCATION_NAME,
        "records": [data_service.row_to_dict(r) for _, r in df.iterrows()],
    }


@router.get("/rainfall/summary")
def rainfall_summary():
    return {**data_service.get_summary(), "source": DATA_SOURCE, "location": LOCATION_NAME}


@router.get("/rainfall/trends")
def rainfall_trends(
    granularity: Literal["daily", "monthly", "annual"] = "monthly",
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    _check_date(start, "start")
    _check_date(end, "end")
    return {
        "granularity": granularity,
        "unit": "mm",
        "points": data_service.get_trends(granularity, start, end),
        "source": DATA_SOURCE,
    }


@router.get("/areas", response_model=list[Area])
def areas():
    return area_service.list_areas()


@router.get("/areas/{area_id}")
def area_detail(area_id: str):
    area = area_service.get_area(area_id)
    if area is None:
        raise HTTPException(404, f"Area '{area_id}' not found")
    latest = data_service.get_latest()
    r = risk_service.assess(latest["rainfall_mm"], latest["rain_3d_mm"], latest["rain_7d_mm"])
    return {
        **area,
        "observation": latest,
        "assessment": {"category": r["category"], "label": r["label"],
                       "triggered_rules": r["triggered_rules"]},
        "advisories": advisory_service.get_advisories(r["category"]),
        "source": DATA_SOURCE,
    }


@router.get("/risk/assessment", response_model=RiskAssessment)
def risk_assessment(date: Optional[str] = Query(None, description="YYYY-MM-DD; default = latest")):
    _check_date(date, "date")
    if date is None:
        row = data_service.load_df().iloc[-1]
    else:
        row = data_service.get_row(date)
        if row is None:
            raise HTTPException(404, f"No data for {date}")
    obs = data_service.row_to_dict(row)
    result = risk_service.assess(obs["rainfall_mm"], obs["rain_3d_mm"], obs["rain_7d_mm"])
    return {
        **result,
        "assessed_for_date": obs["date"],
        "advisories": advisory_service.get_advisories(result["category"]),
        "data_source": DATA_SOURCE,
    }


@router.get("/advisories")
def advisories(category: Optional[Literal["low", "moderate", "high", "unknown"]] = None):
    if category:
        return {"category": category, "advisories": advisory_service.get_advisories(category),
                "note": "General precautions, not official alerts."}
    return {
        "note": "General precautions, not official alerts.",
        "by_category": {c: advisory_service.get_advisories(c)
                        for c in ("low", "moderate", "high")},
    }
