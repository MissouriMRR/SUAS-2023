"""
Defines and implements the Point class used in obstacle_avoidance.py
"""

import time
from dataclasses import dataclass

import mavsdk.telemetry

import utm

# Input points are dicts with time and UTM coordinate data
# May change in the future
InputPoint = dict[str, float | int | str]


@dataclass
class Point:
    """
    A point in 3D space

    Attributes
    ----------
    utm_x : float
        The x-coordinate of this point, in meters, in UTM coordinates
    utm_y : float
        The y-coordinate of this point, in meters, in UTM coordinates
    utm_zone_number : int
        The UTM zone this point is in
    utm_zone_letter : str
        The letter of the UTM latitude band
    altitude : float
        The altitude of the point above sea level, in meters
    time : float | None
        The time at which an object was at this point, in Unix time
    """

    utm_x: float
    utm_y: float
    utm_zone_number: int
    utm_zone_letter: str
    altitude: float
    time: float

    @classmethod
    def from_dict(cls, position_data: InputPoint) -> "Point":
        """
        Factory method accepting a dict with position data

        Parameters
        ----------
        position_data : dict[str, Union[float, int, str]]
            A dict containing at least the following keys:
            'utm_x', 'utm_y', 'utm_zone_number', 'utm_zone_letter'

        Returns
        -------
        A new Point object
        """

        return cls(
            float(position_data["utm_x"]),
            float(position_data["utm_y"]),
            int(position_data["utm_zone_number"]),
            str(position_data["utm_zone_letter"]),
            float(position_data["altitude"]),
            float(position_data["time"]),
        )

    @classmethod
    def from_mavsdk_position(cls, position: mavsdk.telemetry.Position) -> "Point":
        """
        Factory method accepting a mavsdk.telemetry.Position object

        Parameters
        ----------
        position : mavsdk.telemetry.Position
            A position from MAVSDK

        Returns
        -------
        A new Point object
        """

        easting: float
        northing: float
        zone_number: int
        zone_letter: str
        # Can't unpack tuple because mypy complains
        easting, northing, zone_number, zone_letter = utm.from_latlon(
            position.latitude_deg, position.longitude_deg
        )

        # Use time.time() as the time for the point
        return cls(
            easting, northing, zone_number, zone_letter, position.absolute_altitude_m, time.time()
        )
