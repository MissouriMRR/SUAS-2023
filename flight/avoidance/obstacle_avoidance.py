"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

import math
import time

import mavsdk
import mavsdk.telemetry

from .point import Point, InputPoint
from .velocity import Velocity


async def calculate_avoidance_velocity(
    drone: mavsdk.System,
    obstacle_data: list[InputPoint],
    avoidance_radius: float = 10.0,
    avoidance_speed: float = 5.0,
    change_down_vel: bool = False,
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
    avoidance_radius : float = 10.0
        The distance between the drone and obstacle, in meters, at which
        obstacle avoidance will activate
    avoidance_speed : float = 5.0
        The speed, in m/s, at which we should move away from the obstacle
    change_down_vel : bool = False
        Whether to change the vertical velocity

    Returns
    -------
    avoidance_velocity : Velocity | None
        The velocity the drone should move at to avoid the obstacle
        if obstacle avoidance should activate, otherwise None
    """

    if not obstacle_data:
        # No obstacles found
        return None

    if len(obstacle_data) == 1:
        raise ValueError(
            "Expected obstacle_data to have a length of 0 or at least 2; "
            f"got a length of {len(obstacle_data)}"
        )

    # Get position of drone
    drone_position: mavsdk.telemetry.Position = await anext(drone.telemetry.position())

    # Convert drone position to Point object
    drone_position: Point = Point.from_mavsdk_position(drone_position)  # type: ignore

    # Convert obstacle data to list of Point objects
    obstacle_positions: list[Point] = [
        Point.from_dict(
            in_point,
            force_zone_number=drone_position.utm_zone_number,
            force_zone_letter=drone_position.utm_zone_letter,
        )
        for in_point in obstacle_data
    ]

    # Check if all positions are in the same UTM zone
    # Should only error if the utm module isn't working properly
    point: Point
    for point in obstacle_positions:
        if (
            point.utm_zone_letter != drone_position.utm_zone_letter
            or point.utm_zone_number != drone_position.utm_zone_number
        ):
            raise ValueError(
                "Points are in different UTM zones\n"
                "Note: this error should not occur. The utm module should have prevented this."
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
    drone_velocity: mavsdk.telemetry.VelocityNed = await anext(drone.telemetry.velocity_ned())

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

    # Extrapolate current obstacle position based on last known position and estimated velocity
    current_time: float = time.time()
    elapsed_time: float = current_time - obstacle_positions[-1].time
    estimated_obstacle_position: Point = Point(
        utm_x=obstacle_positions[-1].utm_x + elapsed_time * drone_velocity.east_vel,
        utm_y=obstacle_positions[-1].utm_y + elapsed_time * drone_velocity.north_vel,
        utm_zone_number=obstacle_positions[-1].utm_zone_number,
        utm_zone_letter=obstacle_positions[-1].utm_zone_letter,
        altitude=obstacle_positions[-1].altitude - elapsed_time * drone_velocity.down_vel,
        time=current_time,
    )

    # Get the relative velocity we want
    desired_relative_velocity = (
        avoidance_speed
        * Velocity(
            drone_position.utm_y - estimated_obstacle_position.utm_y,
            drone_position.utm_x - estimated_obstacle_position.utm_x,
            estimated_obstacle_position.altitude - drone_position.altitude
            # Altitudes reversed because we want downward velocity
        ).normalized()
    )

    # Get the amount by which we should correct the drone's velocity
    correction_velocity: Velocity = desired_relative_velocity - relative_velocity
    if not change_down_vel:
        correction_velocity = Velocity(
            correction_velocity.north_vel, correction_velocity.east_vel, 0.0
        )

    # Get the velocity at which the drone should move to avoid the obstacle
    avoidance_velocity: Velocity = drone_velocity + correction_velocity

    return avoidance_velocity
