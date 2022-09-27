"""
Contains a moving obstacle avoidance function
"""

from dataclasses import dataclass
from typing import Optional

from mavsdk import System
from mavsdk.telemetry import Position

# TODO: Update type to the correct type # pylint: disable=fixme
Obstacle = dict[str, float]


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
    """

    utm_x: float
    utm_y: float
    utm_zone_number: int
    utm_zone_letter: str


async def calculate_avoidance_path(
    drone: System, obstacle: Obstacle, position: Optional[Position]
) -> list[Point]:
    """
    Given a drone and a moving obstacle, calculates a path avoiding the obstacle

    Parameters
    ----------
    drone : System
        The drone for which the path will be calculated for
    obstacle : dict
        The obstacle to avoid
    position : Optional[Position] = None
        The position of the drone
        The current position of the drone will be used if not provided

    Returns
    -------
    avoidance_path : list[dict]
        The avoidance path, consisting of a list of waypoints
    """

    # Get position of drone
    drone_position: Position
    if position is None:
        async for position in drone.telemetry.position():
            drone_position = position
            break
    else:
        drone_position = position

    # TODO: Do something useful with these variables # pylint: disable=fixme
    print(obstacle, drone_position)

    raise NotImplementedError


def main() -> None:
    """
    Will do something in the future
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
