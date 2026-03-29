"""
Prepare training data from the NYC Taxi Trip Duration dataset (Kaggle).

Reads the raw ~1.46M-row CSV, engineers features relevant to EcoStream
delivery speed prediction, filters outliers, and outputs a clean
downsampled CSV for model training.

Dataset: https://www.kaggle.com/competitions/nyc-taxi-trip-duration
Source: 2016 NYC Yellow Cab trip records (NYC TLC via Google BigQuery)

Usage:
    python scripts/prepare_training_data.py

Input:  data/raw/train.csv   (~190 MB, 1.46M rows — not committed to git)
Output: data/training_data.csv (~1 MB, 20k rows — committed to git)
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "train.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "training_data.csv"
SAMPLE_SIZE = 20_000
RANDOM_SEED = 42

MIN_DURATION_S = 60
MAX_DURATION_S = 10_800  # 3 hours
MIN_SPEED_KMH = 1.0
MAX_SPEED_KMH = 120.0
MIN_DISTANCE_KM = 0.3
NYC_LAT_BOUNDS = (40.5, 41.0)
NYC_LON_BOUNDS = (-74.3, -73.7)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (mirrors app/engine/forecaster.py)."""
    R = 6371.0
    rlat1, rlon1 = math.radians(lat1), math.radians(lon1)
    rlat2, rlon2 = math.radians(lat2), math.radians(lon2)
    dlat, dlon = rlat2 - rlat1, rlon2 - rlon1
    a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def main() -> None:
    if not RAW_PATH.exists():
        print(f"ERROR: Raw dataset not found at {RAW_PATH}")
        print("Download from https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data")
        print(f"and place train.csv at {RAW_PATH}")
        sys.exit(1)

    print(f"Reading {RAW_PATH} ...")
    df = pd.read_csv(RAW_PATH, parse_dates=["pickup_datetime", "dropoff_datetime"])
    print(f"  Raw rows: {len(df):,}")

    # --- Geographic bounds (NYC metro area) ---
    df = df[
        df["pickup_latitude"].between(*NYC_LAT_BOUNDS)
        & df["pickup_longitude"].between(*NYC_LON_BOUNDS)
        & df["dropoff_latitude"].between(*NYC_LAT_BOUNDS)
        & df["dropoff_longitude"].between(*NYC_LON_BOUNDS)
    ]
    print(f"  After geo filter: {len(df):,}")

    # --- Duration bounds ---
    df = df[df["trip_duration"].between(MIN_DURATION_S, MAX_DURATION_S)]
    print(f"  After duration filter: {len(df):,}")

    # --- Haversine distance ---
    df["distance_km"] = df.apply(
        lambda r: haversine(
            r["pickup_latitude"], r["pickup_longitude"],
            r["dropoff_latitude"], r["dropoff_longitude"],
        ),
        axis=1,
    )
    df = df[df["distance_km"] >= MIN_DISTANCE_KM]
    print(f"  After min-distance filter: {len(df):,}")

    # --- Actual speed ---
    df["duration_hours"] = df["trip_duration"] / 3600.0
    df["speed_kmh"] = df["distance_km"] / df["duration_hours"]
    df = df[df["speed_kmh"].between(MIN_SPEED_KMH, MAX_SPEED_KMH)]
    print(f"  After speed filter: {len(df):,}")

    # --- Time features ---
    df["hour_of_day"] = df["pickup_datetime"].dt.hour
    df["day_of_week"] = df["pickup_datetime"].dt.dayofweek  # 0=Monday
    df["month"] = df["pickup_datetime"].dt.month

    # --- Synthetic priority (Express 20%, Standard 80%) ---
    # Express deliveries use priority routing → ~15-20% faster on average
    rng = np.random.default_rng(RANDOM_SEED)
    is_express = rng.random(len(df)) < 0.20
    df["priority"] = np.where(is_express, "Express", "Standard")
    express_boost = np.where(is_express, rng.uniform(1.10, 1.25, len(df)), 1.0)
    df["speed_kmh"] = df["speed_kmh"] * express_boost

    # --- Downsample ---
    df_out = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=RANDOM_SEED)

    # --- Select final columns ---
    columns = ["distance_km", "hour_of_day", "day_of_week", "month", "priority", "speed_kmh"]
    df_out = df_out[columns].reset_index(drop=True)

    # --- Round for readability ---
    df_out["distance_km"] = df_out["distance_km"].round(3)
    df_out["speed_kmh"] = df_out["speed_kmh"].round(2)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUTPUT_PATH, index=False)
    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"  Rows: {len(df_out):,}")
    print(f"  Columns: {list(df_out.columns)}")
    print("\nFeature summary:")
    print(df_out.describe().round(2).to_string())
    print("\nPriority distribution:")
    print(df_out["priority"].value_counts().to_string())


if __name__ == "__main__":
    main()
