"""
Model loader for delivery speed prediction.

Loads the trained DeliverySpeedPredictor from a .joblib artifact on startup.
Falls back to a heuristic if the model file is missing (e.g. fresh checkout
before running the training pipeline).
"""
import logging
from pathlib import Path
from typing import Any

import joblib

logger = logging.getLogger(__name__)

_model: Any = None
_default_model_path = Path(__file__).resolve().parent.parent.parent / "models" / "speed_model.joblib"

try:
    if _default_model_path.exists():
        _model = joblib.load(_default_model_path)
        logger.info("Loaded speed model from %s", _default_model_path)
except Exception:
    logger.warning("Failed to load speed model; using heuristic fallback")
    _model = None


def predict_speed(
    distance_km: float,
    hour_of_day: int,
    day_of_week: int,
    month: int,
    priority: str,
) -> float:
    """Predict delivery speed in km/h given trip context.

    When the trained model is available, uses a RandomForest pipeline trained
    on NYC taxi trip data.  Otherwise falls back to a time-aware heuristic.
    """
    if _model is not None:
        return float(
            _model.predict(
                distance_km=distance_km,
                hour_of_day=hour_of_day,
                day_of_week=day_of_week,
                month=month,
                priority=priority,
            )
        )

    # Heuristic fallback: base speed adjusted by time-of-day and priority
    base = 15.0
    if 7 <= hour_of_day <= 9 or 16 <= hour_of_day <= 18:
        base = 10.0  # rush hour
    elif 22 <= hour_of_day or hour_of_day <= 5:
        base = 25.0  # off-peak / night

    if priority == "Express":
        base *= 1.3

    return round(base, 1)
