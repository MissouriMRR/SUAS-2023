"""Functions for calculating coordinate degree lengths"""

import numpy as np


def latitude_length(latitude: float) -> float:
    """
    Returns the distance in meters of one degree of latitude at a particular longitude

    Parameter
    ---------
    latitude : float
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
    latitude = np.deg2rad(latitude)

    distance: float = (
        111132.92
        - 559.82 * np.cos(2 * latitude)
        + 1.175 * np.cos(4 * latitude)
        - 0.0023 * np.cos(6 * latitude)
    )

    return distance


def longitude_length(latitude: float) -> float:
    """
    Calculates the distance in meters of one degree of longitude at that longitude

    Parameter
    ---------
    latitude : float
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
    latitude = np.deg2rad(latitude)

    distance: float = (
        111412.84 * np.cos(latitude) - 93.5 * np.cos(3 * latitude) + 0.118 * np.cos(5 * latitude)
    )

    return distance
