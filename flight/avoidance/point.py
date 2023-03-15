"""
Defines and implements the Point class used in obstacle_avoidance.py
"""

from __future__ import annotations
from dataclasses import dataclass
import time
from typing import TypedDict

import mavsdk.telemetry
import utm

from .vector.vector3 import Vector3


class InputPoint(TypedDict):
    """
    A dict representing a point to be passed to obstacle avoidance

    See the Point class docstring for more info on attributes
    """

    utm_x: float
    utm_y: float
    utm_zone_number: int
    utm_zone_letter: str
    altitude: float
    time: float


@dataclass(slots=True)
class Point:
    """
    A point in 3D space and time

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
    time : float
        The time at which an object was at this point, in Unix time
    """

    utm_x: float
    utm_y: float
    utm_zone_number: int
    utm_zone_letter: str
    altitude: float
    time: float

    @classmethod
    def from_typed_dict(
        cls,
        position_data: InputPoint,
        force_zone_number: int | None = None,
        force_zone_letter: str | None = None,
    ) -> Point:
        """
        Factory method accepting a dict with position data

        Parameters
        ----------
        position_data : InputPoint
            A dict containing at least the following keys:
            'utm_x', 'utm_y', 'utm_zone_number', 'utm_zone_letter'
        force_zone_letter : int | None = None
            Forces the UTM zone letter of the resulting Point to a certain value
        force_zone_number : int | None = None
            Forces the UTM zone number of the resulting Point to a certain value

        Returns
        -------
        A new Point object
        """

        utm_x: float = float(position_data["utm_x"])
        utm_y: float = float(position_data["utm_y"])
        utm_zone_number: int = position_data["utm_zone_number"]
        utm_zone_letter: str = position_data["utm_zone_letter"]
        if force_zone_number is not None or force_zone_letter is not None:
            utm_x, utm_y, utm_zone_number, utm_zone_letter = utm.from_latlon(
                *utm.to_latlon(utm_x, utm_y, utm_zone_number, utm_zone_letter),
                force_zone_number=force_zone_number,
                force_zone_letter=force_zone_letter,
            )

        return cls(
            utm_x,
            utm_y,
            utm_zone_number,
            utm_zone_letter,
            float(position_data["altitude"]),
            float(position_data["time"]),
        )

    def as_typed_dict(self) -> InputPoint:
        """
        Converts a Point object to an InputPoint TypedDict

        Returns
        -------
        An InputPoint dict object with the same values
        as this Point object
        """

        return {
            "utm_x": self.utm_x,
            "utm_y": self.utm_y,
            "utm_zone_number": self.utm_zone_number,
            "utm_zone_letter": self.utm_zone_letter,
            "altitude": self.altitude,
            "time": self.time,
        }

    @classmethod
    def from_mavsdk_position(cls, position: mavsdk.telemetry.Position) -> Point:
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
            easting,
            northing,
            zone_number,
            zone_letter,
            position.absolute_altitude_m,
            time.time(),
        )

    def to_vector3(self) -> Vector3:
        """
        Converts a Point object to a Vector3 object

        Returns
        -------
        A new Vector3 object in meters, dropping the
        UTM zone number, UTM zone letter, and time
        """

        return Vector3(self.utm_y, self.utm_x, -self.altitude)
