
from pathlib import Path

import pandas as pd
import requests


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "pune_weather.csv"

# Pune city-centre coordinates
LATITUDE = 18.5204
LONGITUDE = 73.8567

START_DATE = "2020-01-01"
END_DATE = "2025-12-31"

API_URL = "https://archive-api.open-meteo.com/v1/archive"


def download_weather_data():
    """Download and save historical daily weather data for Pune."""

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": [
            "precipitation_sum",
            "temperature_2m_max",
            "temperature_2m_min",
            "wind_speed_10m_max",
        ],
        "timezone": "Asia/Kolkata",
    }

    print("Downloading historical weather data for Pune...")

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()

    except requests.RequestException as error:
        print(f"Download failed: {error}")
        print("Check your internet connection and try again.")
        return

    if "daily" not in result or "time" not in result["daily"]:
        print("The API response does not contain the expected daily data.")
        return

    daily_data = result["daily"]

    required_columns = [
        "time",
        "precipitation_sum",
        "temperature_2m_max",
        "temperature_2m_min",
        "wind_speed_10m_max",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in daily_data
    ]

    if missing_columns:
        print(f"Missing expected columns: {missing_columns}")
        return

    df = pd.DataFrame({
        "date": daily_data["time"],
        "rainfall_mm": daily_data["precipitation_sum"],
        "temperature_max_c": daily_data["temperature_2m_max"],
        "temperature_min_c": daily_data["temperature_2m_min"],
        "wind_speed_max_kmh": daily_data["wind_speed_10m_max"],
    })

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_columns = [
        "rainfall_mm",
        "temperature_max_c",
        "temperature_min_c",
        "wind_speed_max_kmh",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Basic data-quality checks
    df = df.dropna(subset=["date"])
    df = df.sort_values("date")
    df = df.drop_duplicates(subset=["date"], keep="last")

    if df.empty:
        print("No valid weather records were received.")
        return

    if (df["rainfall_mm"].dropna() < 0).any():
        print("Warning: negative rainfall values were found.")

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDownload completed successfully.")
    print(f"Records saved: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Saved file: {OUTPUT_FILE}")

    print("\nFirst five records:")
    print(df.head())

    print("\nMissing values per column:")
    print(df.isnull().sum())


if __name__ == "__main__":
    download_weather_data()
