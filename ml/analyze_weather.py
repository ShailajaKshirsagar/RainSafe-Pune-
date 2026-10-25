
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "pune_weather.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"

CLEAN_FILE = PROCESSED_DIR / "pune_weather_clean.csv"
ANNUAL_FILE = PROCESSED_DIR / "annual_rainfall.csv"
MONTHLY_FILE = PROCESSED_DIR / "monthly_rainfall.csv"

ANNUAL_PLOT = DOCS_DIR / "annual_rainfall.png"
MONTHLY_PLOT = DOCS_DIR / "average_monthly_rainfall.png"

# Reference threshold for heavy daily rainfall
HEAVY_RAINFALL_MM = 64.5


def analyze_weather():
    """Validate weather data and generate initial EDA outputs."""

    if not INPUT_FILE.exists():
        print(f"Dataset not found: {INPUT_FILE}")
        print("Run download_weather.py first.")
        return

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    required_columns = [
        "date",
        "rainfall_mm",
        "temperature_max_c",
        "temperature_min_c",
        "wind_speed_max_kmh",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return

    print("=" * 50)
    print("RAINSAFE PUNE - DATA VALIDATION")
    print("=" * 50)

    print(f"\nOriginal number of rows: {len(df)}")

    # Convert columns to appropriate data types
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_columns = [
        "rainfall_mm",
        "temperature_max_c",
        "temperature_min_c",
        "wind_speed_max_kmh",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Remove invalid dates and duplicate dates
    invalid_dates = df["date"].isna().sum()
    df = df.dropna(subset=["date"])

    duplicate_dates = df["date"].duplicated().sum()
    df = df.drop_duplicates(subset=["date"], keep="last")
    df = df.sort_values("date").reset_index(drop=True)

    print(f"Invalid dates removed: {invalid_dates}")
    print(f"Duplicate dates removed: {duplicate_dates}")

    # Treat physically invalid negative measurements as missing
    for column in ["rainfall_mm", "wind_speed_max_kmh"]:
        invalid_values = (df[column] < 0).sum()
        if invalid_values:
            print(
                f"Invalid negative values in {column}: "
                f"{invalid_values}"
            )
            df.loc[df[column] < 0, column] = float("nan")

    print("\nMissing values in cleaned dataset:")
    print(df[required_columns].isna().sum())

    if df.empty:
        print("No valid records remain after validation.")
        return

    # Save the cleaned dataset separately from the raw file
    df.to_csv(CLEAN_FILE, index=False)

    print(f"\nCleaned records: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to "
          f"{df['date'].max().date()}")
    print(f"Cleaned dataset saved to: {CLEAN_FILE}")

    # Rainfall statistics
    rainfall = df["rainfall_mm"].dropna()

    if rainfall.empty:
        print("No valid rainfall values are available for analysis.")
        return

    print("\n" + "=" * 50)
    print("RAINFALL STATISTICS")
    print("=" * 50)

    print(f"Average daily rainfall: {rainfall.mean():.2f} mm")
    print(f"Maximum daily rainfall: {rainfall.max():.2f} mm")
    print(f"Days with rainfall > 0 mm: {(rainfall > 0).sum()}")
    print(
        f"Days with rainfall >= {HEAVY_RAINFALL_MM} mm: "
        f"{(rainfall >= HEAVY_RAINFALL_MM).sum()}"
    )

    # Annual rainfall totals
    annual = (
        df.groupby(df["date"].dt.year)["rainfall_mm"]
        .sum(min_count=1)
        .rename("annual_rainfall_mm")
        .reset_index()
        .rename(columns={"date": "year"})
    )

    annual.to_csv(ANNUAL_FILE, index=False)

    print("\nAnnual rainfall totals:")
    print(annual.to_string(index=False))

    # Average rainfall for each calendar month across all years
    monthly = (
        df.groupby(df["date"].dt.month)["rainfall_mm"]
        .mean()
        .rename("average_daily_rainfall_mm")
        .reset_index()
        .rename(columns={"date": "month"})
    )

    monthly["month_name"] = monthly["month"].apply(
        lambda month: pd.Timestamp(
            year=2000, month=int(month), day=1
        ).strftime("%B")
    )

    monthly.to_csv(MONTHLY_FILE, index=False)

    print("\nAverage daily rainfall by calendar month:")
    print(monthly.to_string(index=False))

    # Plot annual rainfall
    plt.figure(figsize=(10, 5))
    plt.bar(
        annual["year"].astype(str),
        annual["annual_rainfall_mm"],
    )
    plt.title("Annual Rainfall - Pune")
    plt.xlabel("Year")
    plt.ylabel("Total rainfall (mm)")
    plt.tight_layout()
    plt.savefig(ANNUAL_PLOT, dpi=150)
    plt.close()

    # Plot average daily rainfall by calendar month
    plt.figure(figsize=(10, 5))
    plt.bar(
        monthly["month_name"],
        monthly["average_daily_rainfall_mm"],
    )
    plt.title("Average Daily Rainfall by Month - Pune")
    plt.xlabel("Month")
    plt.ylabel("Average daily rainfall (mm)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(MONTHLY_PLOT, dpi=150)
    plt.close()

    print("\nEDA completed.")
    print(f"Annual rainfall chart: {ANNUAL_PLOT}")
    print(f"Monthly rainfall chart: {MONTHLY_PLOT}")
    print(f"Annual summary CSV: {ANNUAL_FILE}")
    print(f"Monthly summary CSV: {MONTHLY_FILE}")


if __name__ == "__main__":
    analyze_weather()
