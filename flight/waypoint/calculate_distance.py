"""
File containing the calculate_distance function responsible
for calculating how far the drone is from the waypoint
"""

import math
import utm


def calculate_distance(
    lat_deg_1: float,
    lon_deg_1: float,
    altitude_m_1: float,
    lat_deg_2: float,
    lon_deg_2: float,
    altitude_m_2: float,
) -> float:
    """
    Calculate the distance, in meters, between two coordinates

    Parameters
    ----------
    lat_deg_1 : float
        The latitude, in degrees, of the first coordinate.
    lon_deg_1 : float
        The longitude, in degrees, of the first coordinate.
    altitude_m_1 : float
        The altitude, in meters, of the first coordinate.
    lat_deg_2 : float
        The latitude, in degrees, of the second coordinate.
    lon_deg_2 : float
        The longitude, in degrees, of the second coordinate.
    altitude_m_2 : float
        The altitude, in meters, of the second coordinate.

    Returns
    -------
    float
        The distance between the two coordinates.
    """
    easting_2: float
    northing_2: float
    zone_num_2: int
    zone_letter_2: str
    easting_2, northing_2, zone_num_2, zone_letter_2 = utm.from_latlon(lat_deg_2, lon_deg_2)
    easting_1: float
    northing_1: float
    easting_1, northing_1, _, _ = utm.from_latlon(
        lat_deg_1,
        lon_deg_1,
        force_zone_number=zone_num_2,
        force_zone_letter=zone_letter_2,
    )

    return math.hypot(
        easting_1 - easting_2,
        northing_1 - northing_2,
        altitude_m_1 - altitude_m_2,
    )
