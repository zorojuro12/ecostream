"""
Unit tests for the forecaster engine.
Tests the Haversine distance calculation using real-world coordinates.
"""
import pytest

from app.engine.forecaster import calculate_haversine_distance


def test_haversine_sfu_campuses():
    """
    Test Haversine distance calculation using SFU Burnaby and SFU Vancouver campuses.
    
    SFU Burnaby: 49.2781, -122.9199
    SFU Vancouver: 49.2820, -123.1085
    Expected Distance: Approximately 13.72 km
    """
    # SFU Burnaby coordinates
    burnaby_lat = 49.2781
    burnaby_lon = -122.9199
    
    # SFU Vancouver coordinates
    vancouver_lat = 49.2820
    vancouver_lon = -123.1085
    
    # Calculate distance
    distance = calculate_haversine_distance(
        lat1=burnaby_lat,
        lon1=burnaby_lon,
        lat2=vancouver_lat,
        lon2=vancouver_lon
    )
    
    # Expected distance is approximately 13.72 km
    # Using relative tolerance of 0.01 (1%) to account for minor variations
    expected_distance = 13.72
    
    assert distance == pytest.approx(expected_distance, rel=0.01), (
        f"Distance between SFU campuses should be approximately {expected_distance} km, "
        f"but got {distance:.2f} km"
    )
