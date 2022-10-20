"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

from dataclasses import dataclass

import mavsdk
import mavsdk.telemetry
import numpy as np
import utm

# Input points are dicts with time and UTM coordinate data
# May change in the future
InputPoint = dict[str, float | int | str]


# TODO: Maybe move to a different file in this directory
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
    time: float | None

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
            float(position_data["altitude"]),  # TODO: Change key to actual key in data input
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
        easting, northing, zone_number, zone_letter = utm.from_latlon(
            position.latitude_deg, position.longitude_deg
        )

        # Can't directly unpack function return value because mypy complains
        return cls(easting, northing, zone_number, zone_letter, position.absolute_altitude_m, None)


@dataclass
class Velocity:
    """
    A velocity in 3D space

    Attributes
    ----------
    north_vel : float
        Eastward velocity in meters per second
    east_vel : float
        Northward velocity in meters per second
    down_vel : float
        Downward velocity in meters per second
    """

    north_vel: float
    east_vel: float
    down_vel: float

    @classmethod
    def from_mavsdk_velocityned(cls, velocity: mavsdk.telemetry.VelocityNed) -> "Velocity":
        """
        Factory method accepting a mavsdk.telemetry.VelocityNed object

        Parameters
        ----------
        velocity : mavsdk.telemetry.VelocityNed
            A velocity (NED) from MAVSDK

        Returns
        -------
        A new Velocity object
        """

        return cls(velocity.north_m_s, velocity.east_m_s, velocity.down_m_s)


async def calculate_avoidance_path(
    drone: mavsdk.System,
    obstacle_data: list[InputPoint],
    avoidance_radius: float = 10.0,
) -> list[Point]:
    """
    Given a drone and a moving obstacle, calculates a path avoiding the obstacle

    Parameters
    ----------
    drone : mavsdk.System
        The drone for which the path will be calculated for
    obstacle_data : list[InputPoint]
        Positions at previous times of the obstacle (probably another drone)
    avoidance_radius : float
        The radius around the predicted center of the obstacle the drone should avoid

    Returns
    -------
    avoidance_path : list[dict]
        The avoidance path, consisting of a list of waypoints
    """

    # Convert obstacle data to list of Point
    obstacle_positions: list[Point] = [Point.from_dict(in_point) for in_point in obstacle_data]

    # Get position of drone
    raw_drone_position: mavsdk.telemetry.Position
    async for position in drone.telemetry.position():
        raw_drone_position = position
        break

    # Convert drone position to UTM Point
    drone_position: Point = Point.from_mavsdk_position(raw_drone_position)

    # TODO: Make the function work if UTM zones differ
    # Check if all positions are in the same UTM zone
    point: Point
    for point in obstacle_positions:
        if (
            point.utm_zone_letter != drone_position.utm_zone_letter
            or point.utm_zone_number != drone_position.utm_zone_number
        ):
            raise ValueError(
                "Points are in different UTM zones (Note: tell obstacle avoidance team to fix this)"
            )

    # Get velocity of drone
    raw_drone_velocity: mavsdk.telemetry.VelocityNed
    async for velocity in drone.telemetry.velocity_ned():
        raw_drone_velocity = velocity
        break

    # Convert drone position to Velocity object
    # Units don't change, only the type of the object
    drone_velocity: Velocity = Velocity.from_mavsdk_velocityned(raw_drone_velocity)

    obstacle_positions.sort(key=lambda p: p.time or 0.0)

    # Degree of polynomial used in polynomial regression
    polynomial_degree: int = 3
    # Create list of times
    obstacle_times: list[float] = [
        point.time for point in obstacle_positions if point.time is not None
    ]

    # Should hopefully never fail, otherwise I will have a mental breakdown
    assert len(obstacle_times) == len(obstacle_positions)

    # Get weights for polynomial regression
    # The most recent point should have the highest weight
    weights: range = range(
        1, len(obstacle_times) + 1
    )  # For some reason range objects can be reused

    # TODO: Research better models for predicting the obstacle's path
    # Use polynomial regression to model the obstacle's path
    # The polynomial is arr[0] * t**n + arr[1] * t**(n - 1) + ... + arr[n - 1] * t + arr[n]
    x_polynomial: list[float] = list(
        np.polyfit(
            [point.utm_x for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=weights,
        )
    )
    y_polynomial: list[float] = list(
        np.polyfit(
            [point.utm_y for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=weights,
        )
    )
    altitude_polynomial: list[float] = list(
        np.polyfit(
            [point.altitude for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=weights,
        )
    )

    # TODO: Do something useful with these variables
    print(x_polynomial, y_polynomial, altitude_polynomial, drone_velocity, avoidance_radius)

    raise NotImplementedError


def main() -> None:
    """
    Will do something in the future
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
