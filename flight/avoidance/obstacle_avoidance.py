"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

import math

import mavsdk
import mavsdk.telemetry

from point import Point, InputPoint
from velocity import Velocity


async def calculate_avoidance_velocity(
    drone: mavsdk.System,
    obstacle_data: list[InputPoint],
    avoidance_radius: float = 10.0,
    avoidance_speed: float = 5.0,
) -> Velocity | None:
    """
    Given a drone and a moving obstacle, calculates a velocity at which the
    drone should move to avoid the obstacle

    Parameters
    ----------
    drone : mavsdk.System
        The drone for which the path will be calculated for
    obstacle_data : list[InputPoint]
        Positions at previous times of the obstacle (probably another drone)
    avoidance_radius : float
        The distance between the drone and obstacle, in meters, at which
        obstacle avoidance will active
    avoidance_speed : float
        The speed, in m/s, at which we should move away from the obstacle

    Returns
    -------
    avoidance_velocity : Velocity | None
        The velocity the drone should move at to avoid the obstacle
        if obstacle avoidance should activate, otherwise None
    """

    if len(obstacle_data) < 2:
        raise ValueError(
            "Expected obstacle_data to have length of at least 2; "
            f"got a length of {len(obstacle_data)}"
        )

    # Convert obstacle data to list of Point objects
    obstacle_positions: list[Point] = [Point.from_dict(in_point) for in_point in obstacle_data]

    # Get position of drone
    drone_position: mavsdk.telemetry.Position
    async for position in drone.telemetry.position():
        drone_position = position
        break

    # Convert drone position to Point object
    drone_position: Point = Point.from_mavsdk_position(drone_position)  # type: ignore

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

    # Sort obstacle positions with respect to time
    obstacle_positions.sort(key=lambda p: p.time)

    # Check if inside avoidance radius, and return None if not
    if (
        math.hypot(
            drone_position.utm_x - obstacle_positions[-1].utm_x,
            drone_position.utm_y - obstacle_positions[-1].utm_y,
            drone_position.altitude - obstacle_positions[-1].altitude,
        )
        > avoidance_radius
    ):
        return None

    # Get velocity of drone
    drone_velocity: mavsdk.telemetry.VelocityNed
    async for velocity in drone.telemetry.velocity_ned():
        drone_velocity = velocity
        break

    # Convert drone velocity to Velocity object
    # Units don't change, only the type of the object
    drone_velocity: Velocity = Velocity.from_mavsdk_velocityned(drone_velocity)  # type: ignore

    # Estimate obstacle velocity
    obstacle_velocity: Velocity = Velocity(
        obstacle_positions[-1].utm_y - obstacle_positions[-2].utm_y,
        obstacle_positions[-1].utm_x - obstacle_positions[-2].utm_x,
        obstacle_positions[-2].altitude - obstacle_positions[-1].altitude
        # Altitudes reversed because we want downward velocity
    ) / (obstacle_positions[-1].time - obstacle_positions[-2].time)

    # Get velocity of our drone relative to the obstacle
    relative_velocity: Velocity = drone_velocity - obstacle_velocity

    # Get the relative velocity we want
    desired_relative_velocity = (
        avoidance_speed
        * Velocity(
            drone_position.utm_y - obstacle_positions[-1].utm_y,
            drone_position.utm_x - obstacle_positions[-1].utm_x,
            obstacle_positions[-1].altitude - drone_position.altitude
            # Altitudes reversed because we want downward velocity
        ).normalized()
    )

    # Get the amount by which we should correct the drone's velocity
    correction_velocity: Velocity = desired_relative_velocity - relative_velocity

    # Get the velocity at which the drone should move to avoid the obstacle
    avoidance_velocity: Velocity = drone_velocity + correction_velocity

    return avoidance_velocity


def main() -> None:
    """
    Will do something in the future
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
