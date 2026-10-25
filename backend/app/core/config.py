"""Central settings: file paths, CORS, and the editable risk thresholds."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_FILE = PROJECT_ROOT / "data" / "processed" / "pune_features.csv"

CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

DATA_SOURCE = "Open-Meteo Historical Weather API (archive-api.open-meteo.com)"
LOCATION_NAME = "Pune city centre (18.5204, 73.8567)"

# Project-defined operational thresholds (mm). NOT proven flood boundaries.
# Edit these numbers to change the risk rules; no other code needs to change.
THRESHOLDS = {
    "high":     {"rain_1d_mm": 64.5, "rain_3d_mm": 100.0, "rain_7d_mm": 150.0},
    "moderate": {"rain_1d_mm": 35.0, "rain_3d_mm": 60.0,  "rain_7d_mm": 100.0},
}
HEAVY_DAY_MM = 64.5   # daily rainfall counted as a "heavy rainfall day"
RAINY_DAY_MM = 2.5    # daily rainfall counted as a "rainy day"

LIMITATIONS = [
    "Rainfall is not flooding: this indicator does not predict floods.",
    "Data is one city-centre grid point, not a measurement at each neighbourhood.",
    "Thresholds are project-defined, not validated against Pune flood incidents.",
    "Daily values are model-based (Open-Meteo), not official IMD rain-gauge readings.",
]

# ---- Live data (Open-Meteo) ----
LATITUDE = 18.5204
LONGITUDE = 73.8567
TIMEZONE = "Asia/Kolkata"
LIVE_DATA = os.getenv("LIVE_DATA", "true").lower() == "true"
LIVE_CACHE_MINUTES = int(os.getenv("LIVE_CACHE_MINUTES", "30"))
LIVE_TIMEOUT_SECONDS = 10
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
