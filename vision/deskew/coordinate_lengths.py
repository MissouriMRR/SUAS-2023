"""Functions for calculating coordinate degree lengths"""

import numpy as np


def latitude_length(latitude_deg: float) -> float:
    """
    Returns the distance in meters of one degree of latitude at a particular latitude

    Parameters
    ---------
    latitude_deg : float
        The latitude in degrees

    Returns
    -------
    latitude_length
        The length of a degree of latitude in meters at the given latitude

    References
    ----------
    https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    """

    # Convert to radians for trig functions
    latitude_rad: float = np.deg2rad(latitude_deg)

    # Formula is adapted from the referenced Wikipedia page
    distance: float = (
        111132.92
        - 559.82 * np.cos(2 * latitude_rad)
        + 1.175 * np.cos(4 * latitude_rad)
        - 0.0023 * np.cos(6 * latitude_rad)
    )

    return distance


def longitude_length(latitude_deg: float) -> float:
    """
    Calculates the distance in meters of one degree of longitude at that latitude

    Parameters
    ---------
    latitude_deg : float
        The latitude in degrees

    Returns
    -------
    longitude_length
        The length of a degree of longitude in meters at the given latitude

    References
    ----------
    https://en.wikipedia.org/wiki/Geographic_coordinate_system#Length_of_a_degree
    """

    # Convert degrees to radians for trig functions
    latitude_rad: float = np.deg2rad(latitude_deg)

    # Formula is adapted from the referenced Wikipedia page
    distance: float = (
        111412.84 * np.cos(latitude_rad)
        - 93.5 * np.cos(3 * latitude_rad)
        + 0.118 * np.cos(5 * latitude_rad)
    )

    return distance
