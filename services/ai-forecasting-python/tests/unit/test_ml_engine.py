"""
Unit tests for the multi-feature delivery speed prediction engine.

Tests both the trained model path and the heuristic fallback, verifying
that time-of-day and priority produce expected speed relationships.
"""
from unittest.mock import MagicMock, patch

import app.engine.model_loader as ml


class TestPredictSpeedWithModel:
    """Tests when the trained .joblib model is available."""

    def test_express_faster_than_standard_at_same_time(self):
        speed_express = ml.predict_speed(
            distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Express",
        )
        speed_standard = ml.predict_speed(
            distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Standard",
        )
        assert speed_express > speed_standard, (
            f"Express ({speed_express:.1f}) should be faster than Standard ({speed_standard:.1f})"
        )

    def test_offpeak_faster_than_rush_hour(self):
        rush = ml.predict_speed(
            distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Standard",
        )
        offpeak = ml.predict_speed(
            distance_km=5.0, hour_of_day=2, day_of_week=2, month=3, priority="Standard",
        )
        assert offpeak > rush, (
            f"Off-peak 2am ({offpeak:.1f}) should be faster than rush 8am ({rush:.1f})"
        )

    def test_returns_positive_float(self):
        speed = ml.predict_speed(
            distance_km=10.0, hour_of_day=14, day_of_week=4, month=6, priority="Standard",
        )
        assert isinstance(speed, float)
        assert speed > 0

    def test_model_used_when_loaded(self):
        mock_model = MagicMock()
        mock_model.predict.return_value = 18.5

        with patch.object(ml, "_model", mock_model):
            result = ml.predict_speed(
                distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Standard",
            )

        mock_model.predict.assert_called_once_with(
            distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Standard",
        )
        assert result == 18.5


class TestPredictSpeedHeuristicFallback:
    """Tests the fallback when no .joblib model is loaded."""

    def test_rush_hour_slower_than_offpeak(self):
        with patch.object(ml, "_model", None):
            rush = ml.predict_speed(
                distance_km=5.0, hour_of_day=8, day_of_week=2, month=3, priority="Standard",
            )
            night = ml.predict_speed(
                distance_km=5.0, hour_of_day=2, day_of_week=2, month=3, priority="Standard",
            )
        assert night > rush

    def test_express_faster_than_standard_in_fallback(self):
        with patch.object(ml, "_model", None):
            express = ml.predict_speed(
                distance_km=5.0, hour_of_day=14, day_of_week=2, month=3, priority="Express",
            )
            standard = ml.predict_speed(
                distance_km=5.0, hour_of_day=14, day_of_week=2, month=3, priority="Standard",
            )
        assert express > standard

    def test_fallback_returns_positive(self):
        with patch.object(ml, "_model", None):
            speed = ml.predict_speed(
                distance_km=3.0, hour_of_day=12, day_of_week=0, month=1, priority="Standard",
            )
        assert speed > 0
