"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

from dataclasses import dataclass
from typing import Optional
from typing import Union

from mavsdk import System
from mavsdk.telemetry import Position as MavsdkPosition

import utm


# Input points are dicts with time and UTM coordinate data
# May change in the future
# Optional[float] for time, allows type to be used for points without time
InputPoint = dict[str, Union[float, int, str, Optional[float]]]


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
    altitude: Optional[float]

    @classmethod
    def from_dict(cls, position_data: InputPoint) -> "Point":
        """
        Converts a dict with position data to a Point object

        Parameters
        ----------
        position_data : dict[str, Union[float, int, str]]
            A dict containing at least the following keys:
            'utm_x', 'utm_y', 'utm_zone_number', 'utm_zone_letter'

        Returns
        -------
        A new Point object
        """

        # TODO: Fix pylint errors
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
        Converts a position data dict to a Point object

        Parameters
        ----------
        position : mavsdk.telemetry.Position
            A position from MAVSDK

        Returns
        -------
        A new Point object
        """

        # TODO: Fix pylint errors
        return cls(*utm.from_latlon(position.latitude_deg, position.longitude_deg), None)


async def calculate_avoidance_path(
    drone: System,
    obstacle_data: list[InputPoint],
    position: Optional[MavsdkPosition],
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
    position : Optional[Position] = None
        The position of the drone
        The current position of the drone will be used if not provided
    avoidance_radius : float
        The radius of the sphere, in meters, from the predicted center of the obstacle that the drone should avoid

    Returns
    -------
    avoidance_path : list[dict]
        The avoidance path, consisting of a list of waypoints
    """

    # Get position of drone
    raw_drone_position: MavsdkPosition
    if position is None:
        async for position in drone.telemetry.position():
            raw_drone_position = position
            break
    else:
        raw_drone_position = position

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
