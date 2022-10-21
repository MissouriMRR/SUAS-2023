"""
Contains a moving obstacle avoidance function
"""

# pylint: disable=fixme

from typing import Callable

import mavsdk
import mavsdk.telemetry
import numpy as np

from point import Point, InputPoint
from velocity import Velocity


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
    drone_position: mavsdk.telemetry.Position
    async for position in drone.telemetry.position():
        drone_position = position
        break

    # Convert drone position to UTM Point
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

    # Get velocity of drone
    drone_velocity: mavsdk.telemetry.VelocityNed
    async for velocity in drone.telemetry.velocity_ned():
        drone_velocity = velocity
        break

    # Convert drone position to Velocity object
    # Units don't change, only the type of the object
    drone_velocity: Velocity = Velocity.from_mavsdk_velocityned(drone_velocity)  # type: ignore

    obstacle_positions.sort(key=lambda p: p.time)

    # Degree of polynomial used in polynomial regression
    polynomial_degree: int = 3
    # Create list of times
    obstacle_times: list[float] = [point.time for point in obstacle_positions]

    # TODO: Research better models for predicting the obstacle's path
    # Use polynomial regression to model the obstacle's path
    # The polynomial is arr[0] * t**n + arr[1] * t**(n - 1) + ... + arr[n - 1] * t + arr[n]
    x_polynomial: list[float] = list(
        np.polyfit(
            [point.utm_x for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=range(1, len(obstacle_times) + 1),
        )
    )
    y_polynomial: list[float] = list(
        np.polyfit(
            [point.utm_y for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=range(1, len(obstacle_times) + 1),
        )
    )
    altitude_polynomial: list[float] = list(
        np.polyfit(
            [point.altitude for point in obstacle_positions],
            obstacle_times,
            polynomial_degree,
            w=range(1, len(obstacle_times) + 1),
        )
    )

    def polynomial_evaluator(coefficients: list[float]) -> Callable[[float], float]:
        def evaluate(val: float) -> float:
            result: float = 0.0
            coefficient: float
            for coefficient in coefficients:
                result *= val
                result += coefficient
            return result

        return evaluate

    predict_x: Callable[[float], float] = polynomial_evaluator(x_polynomial)
    predict_y: Callable[[float], float] = polynomial_evaluator(y_polynomial)
    predict_altitude: Callable[[float], float] = polynomial_evaluator(altitude_polynomial)

    # TODO: Do something useful with these variables
    print(x_polynomial, y_polynomial, altitude_polynomial, drone_velocity, avoidance_radius)
    print(
        predict_x(drone_position.time),
        predict_y(drone_position.time),
        predict_altitude(drone_position.time),
    )

    raise NotImplementedError


def main() -> None:
    """
    Will do something in the future
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
