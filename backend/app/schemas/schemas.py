from typing import Dict, List, Optional

from pydantic import BaseModel


class Observation(BaseModel):
    date: str
    rainfall_mm: Optional[float]
    temperature_max_c: Optional[float]
    temperature_min_c: Optional[float]
    wind_speed_max_kmh: Optional[float]
    rain_3d_mm: Optional[float]
    rain_7d_mm: Optional[float]
    data_type: str = "daily_observation"
    is_live: bool = False
    source: str
    location: str


class Area(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    rainfall_basis: str
    coordinate_note: str
    rainfall_note: str


class RiskAssessment(BaseModel):
    category: str
    label: str
    assessed_for_date: str
    measurements: Dict[str, Optional[float]]
    missing_measurements: List[str]
    triggered_rules: List[str]
    thresholds_used: Dict[str, Dict[str, float]]
    methodology: str
    limitations: List[str]
    advisories: List[str]
    data_source: str
