"""
Pure ML/Forecasting logic engine.
Strict Rule: No I/O or Database calls allowed here.
"""
import math


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    This is a pure function with no external dependencies or I/O operations.
    
    Args:
        lat1: Latitude of the first point in degrees
        lon1: Longitude of the first point in degrees
        lat2: Latitude of the second point in degrees
        lon2: Longitude of the second point in degrees
        
    Returns:
        Distance in kilometers between the two points
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad)
        * math.cos(lat2_rad)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance_km = R * c
    
    return distance_km
