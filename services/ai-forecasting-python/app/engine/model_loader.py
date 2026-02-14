"""
Model loader for priority-based speed prediction.
Loads .joblib model on startup; falls back to hardcoded logic if file missing.
"""
from pathlib import Path
from typing import Any

import joblib

# Load model on startup; None = use hardcoded fallback
_model: Any = None
_default_model_path = Path(__file__).resolve().parent.parent.parent / "models" / "speed_model.joblib"

try:
    if _default_model_path.exists():
        _model = joblib.load(_default_model_path)
except Exception:
    _model = None


def predict_speed(priority: str) -> float:
    """
    Return predicted speed in km/h for the given priority.
    Express = faster (60 km/h), Standard = slower (30 km/h).
    """
    if _model is not None:
        return float(_model.predict(priority))
    if priority == "Express":
        return 60.0
    return 30.0  # Standard
