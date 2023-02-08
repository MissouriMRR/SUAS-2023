"""
Contains a goto function that incorporates obstacle avoidance
Use instead of goto_location from MAVSDK
"""

import asyncio
from asyncio import Task
from typing import AsyncIterator

import mavsdk
import mavsdk.telemetry

from .obstacle_avoidance import calculate_avoidance_velocity
from .point import InputPoint
from .velocity import Velocity


async def goto_with_avoidance(
    drone: mavsdk.System,
    latitude_deg: float,
    longitude_deg: float,
    absolute_altitude_m: float,
    yaw_deg: float,
    position_updates: AsyncIterator[list[InputPoint]],
    avoidance_radius: float = 10.0,
    avoidance_speed: float = 5.0,
) -> None:
    """
    A goto function with obstacle avoidance intended to replace
    goto_location from mavsdk

    Parameters
    ----------
    drone : mavsdk.System
        The drone that should go to the location
    latitude_deg : float
        Same as in goto_location
    longitude_deg : float
        Same as in goto_location
    absolute_altitude_m : float
        Same as in goto_location
    yaw_deg : float
        Same as in goto_location
    position_updates : AsyncIterator[list[InputPoint]]
        Position updates for the obstacle to avoid;
        for best results, this should yield frequently
    avoidance_radius : float = 10.0
        The distance between the drone and obstacle, in meters, at which
        obstacle avoidance will activate
    avoidance_speed : float = 5.0
        The speed, in m/s, at which we should move away from the obstacle
    """

    # Function to create a goto task for the drone
    async def restart_goto() -> Task[None]:
        new_yaw: float = await anext(drone.telemetry.heading())
        return asyncio.ensure_future(
            drone.action.goto_location(latitude_deg, longitude_deg, absolute_altitude_m, new_yaw)
        )

    # Start going to the location
    goto_task: Task[None] = asyncio.ensure_future(
        drone.action.goto_location(latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
    )

    try:
        while not goto_task.done():
            # Get next list of obstacle positions
            obstacle_positions: list[InputPoint] = await anext(position_updates)

            # Calculate avoidance velocity
            avoidance_velocity: Velocity | None = await calculate_avoidance_velocity(
                drone, obstacle_positions, avoidance_radius, avoidance_speed, False
            )

            # If no avoidance is needed, restart goto and continue
            if avoidance_velocity is None:
                if goto_task.cancelled():
                    goto_task = await restart_goto()
                continue

            # Cancel goto then change velocity to avoid the obstacle
            goto_task.cancel()
            await drone.offboard.set_velocity_ned(avoidance_velocity.to_mavsdk_velocitynedyaw())
    finally:
        # Cancel goto_task if this task is canceled
        goto_task.cancel()
