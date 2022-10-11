"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

from dataclasses import dataclass

from mavsdk import System
from mavsdk.telemetry import Position as MavsdkPosition

import utm


# Input points are dicts with time and UTM coordinate data
# May change in the future
InputPoint = dict[str, float | int | str]


# TODO: Maybe add a time component
# TODO: Maybe move to a different file in this directory
@dataclass
class Point:
    """
    A point in 3D space

    Attributes
    ----------
    utm_x : float
        The x-coordinate of this point in the UTM coordinate system
    utm_y : float
        The y-coordinate of this point in the UTM coordinate system
    utm_zone_number : int
        The UTM zone this point is in
    utm_zone_letter : str
        The letter of the UTM latitude band
    altitude : float
        The altitude of the point above sea level, in meters
    """

    utm_x: float
    utm_y: float
    utm_zone_number: int
    utm_zone_letter: str
    altitude: float | None

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
            None,
        )

    @classmethod
    def from_mavsdk_position(cls, position: MavsdkPosition) -> "Point":
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
        easting, northing, zone_number, zone_letter = utm.from_latlon(
            position.latitude_deg, position.longitude_deg
        )

        # Can't directly unpack function return value because mypy complains
        return cls(easting, northing, zone_number, zone_letter, position.absolute_altitude_m)


async def calculate_avoidance_path(
    drone: System,
    obstacle_data: list[InputPoint],
    avoidance_radius: float = 10.0,
) -> list[Point]:
    """
    Given a drone and a moving obstacle, calculates a path avoiding the obstacle

    Parameters
    ----------
    drone : System
        The drone for which the path will be calculated for
    obstacle_data : list[InputPoint]
        Previously known positions
    avoidance_radius : float
        The radius around the predicted center of the obstacle the drone should avoid

    Returns
    -------
    avoidance_path : list[dict]
        The avoidance path, consisting of a list of waypoints
    """

    # Get position of drone
    raw_drone_position: MavsdkPosition
    async for position in drone.telemetry.position():
        raw_drone_position = position
        break

    # Convert drone position to UTM Point
    drone_position: Point = Point.from_mavsdk_position(raw_drone_position)

    # TODO: Do something useful with these variables
    print(obstacle_data, drone_position, avoidance_radius)

    raise NotImplementedError


def main() -> None:
    """
    Will do something in the future
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
