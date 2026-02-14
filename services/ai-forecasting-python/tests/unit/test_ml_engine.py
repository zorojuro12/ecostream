"""
Unit tests for the ML-based speed prediction engine.
Asserts priority-based travel time: Express = faster, Standard = slower.
"""

from app.engine.model_loader import predict_speed


def test_priority_based_travel_time_express_faster_than_standard():
    """
    Assert that the forecaster can predict travel time based on distance AND priority:
    Express = faster speed (60 km/h), Standard = slower speed (30 km/h).
    Travel time (minutes) = (distance_km / speed_kmh) * 60.
    """
    speed_express = predict_speed("Express")
    speed_standard = predict_speed("Standard")

    assert speed_express == 60.0, "Express priority should yield 60 km/h"
    assert speed_standard == 30.0, "Standard priority should yield 30 km/h"

    distance_km = 60.0
    travel_time_express_min = (distance_km / speed_express) * 60
    travel_time_standard_min = (distance_km / speed_standard) * 60

    assert travel_time_express_min == 60.0, "60 km at 60 km/h = 60 minutes"
    assert travel_time_standard_min == 120.0, "60 km at 30 km/h = 120 minutes"
    assert travel_time_express_min < travel_time_standard_min, "Express should be faster than Standard"


def test_priority_based_speed_with_mocked_joblib_model():
    """
    Mock a joblib model and assert predict_speed uses it: Express -> 60, Standard -> 30.
    """
    from unittest.mock import patch, MagicMock

    mock_model = MagicMock()
    mock_model.predict.side_effect = lambda x: 60.0 if x == "Express" else 30.0

    import app.engine.model_loader as ml

    with patch.object(ml, "_model", mock_model):
        assert ml.predict_speed("Express") == 60.0
        assert ml.predict_speed("Standard") == 30.0
        assert mock_model.predict.call_count >= 2
