"""Add rolling 3-day / 7-day rainfall totals to the cleaned dataset.

Run from the project root:  python ml/build_features.py
"""
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "processed" / "pune_weather_clean.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "pune_features.csv"

HEAVY_RAINFALL_MM = 64.5


def get_season(month):
    """Indian meteorological seasons."""
    if month in (1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "pre_monsoon"
    if month in (6, 7, 8, 9):
        return "monsoon"
    return "post_monsoon"


def add_rolling_features(df):
    """A window is calculated only when ALL days in it have a value.
    Missing days are never treated as zero."""
    df = df.sort_values("date").set_index("date")
    full_range = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_range)  # missing calendar days become NaN
    df.index.name = "date"
    df["rain_3d_mm"] = df["rainfall_mm"].rolling(3, min_periods=3).sum()
    df["rain_7d_mm"] = df["rainfall_mm"].rolling(7, min_periods=7).sum()
    df["is_heavy_day"] = df["rainfall_mm"] >= HEAVY_RAINFALL_MM
    df["season"] = df.index.month.map(get_season)
    return df.reset_index()


def main():
    if not INPUT_FILE.exists():
        print(f"Missing {INPUT_FILE}. Run ml/analyze_weather.py first.")
        return
    df = pd.read_csv(INPUT_FILE, parse_dates=["date"])
    features = add_rolling_features(df)
    features.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(features)} rows to {OUTPUT_FILE}")
    print(f"Max 3-day rainfall: {features['rain_3d_mm'].max():.1f} mm")
    print(f"Max 7-day rainfall: {features['rain_7d_mm'].max():.1f} mm")


if __name__ == "__main__":
    main()
