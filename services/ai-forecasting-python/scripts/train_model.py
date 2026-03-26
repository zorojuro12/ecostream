"""
Train the EcoStream delivery speed prediction model.

Trains a scikit-learn pipeline on features derived from the NYC Taxi Trip
Duration dataset (see prepare_training_data.py).  The model predicts
delivery speed (km/h) given distance, time-of-day, day-of-week, month,
and order priority.

Usage:
    python scripts/train_model.py

Input:  data/training_data.csv  (produced by prepare_training_data.py)
Output: models/speed_model.joblib
"""
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "training_data.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "speed_model.joblib"

FEATURE_COLS = ["distance_km", "hour_of_day", "day_of_week", "month", "priority"]
TARGET_COL = "speed_kmh"
NUMERIC_FEATURES = ["distance_km", "hour_of_day", "day_of_week", "month"]
CATEGORICAL_FEATURES = ["priority"]

RANDOM_SEED = 42
TEST_SIZE = 0.20


class DeliverySpeedPredictor:
    """Wrapper providing a clean predict() interface for the application layer.

    Accepts individual feature values and returns a single speed prediction.
    The underlying sklearn pipeline handles encoding and scaling internally.
    """

    def __init__(self, pipeline: Pipeline, feature_names: list[str]) -> None:
        self.pipeline = pipeline
        self.feature_names = feature_names

    def predict(
        self,
        distance_km: float,
        hour_of_day: int,
        day_of_week: int,
        month: int,
        priority: str,
    ) -> float:
        row = pd.DataFrame(
            [[distance_km, hour_of_day, day_of_week, month, priority]],
            columns=self.feature_names,
        )
        return float(self.pipeline.predict(row)[0])


def main() -> None:
    if not DATA_PATH.exists():
        print(f"ERROR: Training data not found at {DATA_PATH}")
        print("Run  python scripts/prepare_training_data.py  first.")
        raise SystemExit(1)

    print(f"Loading {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    print(f"  Rows: {len(df):,}  Columns: {list(df.columns)}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED,
    )
    print(f"  Train: {len(X_train):,}  Test: {len(X_test):,}")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=10,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )),
    ])

    print("Training RandomForestRegressor ...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = r2_score(y_test, y_pred)

    print(f"\n--- Evaluation (test set, {len(X_test):,} rows) ---")
    print(f"  MAE:  {mae:.2f} km/h")
    print(f"  RMSE: {rmse:.2f} km/h")
    print(f"  R²:   {r2:.4f}")

    # Sanity checks: rush-hour vs off-peak, Express vs Standard
    wrapper = DeliverySpeedPredictor(pipeline, FEATURE_COLS)
    baseline = {"distance_km": 5.0, "month": 3, "day_of_week": 2}

    rush_std = wrapper.predict(hour_of_day=8, priority="Standard", **baseline)
    offpeak_std = wrapper.predict(hour_of_day=2, priority="Standard", **baseline)
    rush_exp = wrapper.predict(hour_of_day=8, priority="Express", **baseline)

    print(f"\n--- Sanity checks (5 km, March, Wednesday) ---")
    print(f"  Rush-hour Standard (8am):  {rush_std:.1f} km/h")
    print(f"  Off-peak  Standard (2am):  {offpeak_std:.1f} km/h")
    print(f"  Rush-hour Express  (8am):  {rush_exp:.1f} km/h")
    print(f"  Express faster than Standard at rush hour: {rush_exp > rush_std}")
    print(f"  Off-peak faster than rush hour:            {offpeak_std > rush_std}")

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(wrapper, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    print(f"  Size: {MODEL_PATH.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
