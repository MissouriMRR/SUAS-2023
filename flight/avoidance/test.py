"""
Test code for our drone in obstacle avoidance
"""

import asyncio
import dataclasses
import random
from typing import AsyncIterator

import mavsdk
import mavsdk.core
import mavsdk.telemetry

from .avoidance_goto import goto_with_avoidance
from .point import InputPoint, Point

TAKEOFF_ALTITUDE: float = 20.0
DEFAULT_SPREAD_LATLON: float = 5e-5
DEFAULT_SPREAD_ALTITUDE: float = 8.0


async def random_position(
    drone: mavsdk.System, spread_latlon: float, spread_altitude: float
) -> tuple[float, float, float]:
    """
    Generates a random position relative to a drone's current position

    Parameters
    ----------
    drone : mavsdk.System
        The drone to generate a random position relative to
    spread_latlon : float
        The spread, in degrees, from the drone's lat/lon
        in which a random lat/lon may be generated
    spread_altitude : float
        The spread, in meters, from the drone's altitude
        in which a random altitude may be generated

    Returns
    -------
    A random, uniformly distributed position relative to the drone's position
    """

    position: mavsdk.telemetry.Position = await anext(drone.telemetry.position())
    return (
        position.latitude_deg + 2 * spread_latlon * (random.random() - 0.5),
        position.longitude_deg + 2 * spread_latlon * (random.random() - 0.5),
        position.absolute_altitude_m + 2 * spread_altitude * (random.random() - 0.5),
    )


async def drone_positions(drone: mavsdk.System) -> AsyncIterator[list[InputPoint]]:
    """
    Gives periodic position updates for a drone;
    in actual use, the camera and vision code would
    be used to determine the position of the drone
    to avoid

    Parameters
    ----------
    drone : mavsdk.System
        The drone to get position updates from

    Returns
    -------
    An async iterator yielding the drone's previous
    and current positions as a list of UTM coordinates with time
    """

    positions: list[InputPoint] = []

    while True:
        point: Point = Point.from_mavsdk_position(await anext(drone.telemetry.position()))
        in_point: InputPoint = dataclasses.asdict(point)

        if len(positions) > 4:
            positions = positions[1:]

        positions.append(in_point)

        print(positions)
        yield positions[:]
        await asyncio.sleep(1.0)


async def avoiding_drone_test(
    drone: mavsdk.System, position_updates: AsyncIterator[list[InputPoint]]
) -> None:
    """
    Runs test code for the drone trying to avoid the other drone
    """

    asyncio.ensure_future(print_status_text(drone))

    state: mavsdk.core.ConnectionState
    async for state in drone.core.connection_state():
        if state.is_connected:
            break

    health: mavsdk.telemetry.Health
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break

    await drone.action.arm()
    await drone.action.set_takeoff_altitude(TAKEOFF_ALTITUDE)
    await drone.action.takeoff()

    await goto_with_avoidance(drone, 0.0, 0.0, 100.0, 0.0, position_updates)


async def drone_to_avoid_test(drone: mavsdk.System) -> None:
    """
    Runs test code for the drone which the other drone should avoid
    """

    asyncio.ensure_future(print_status_text(drone))

    state: mavsdk.core.ConnectionState
    async for state in drone.core.connection_state():
        if state.is_connected:
            break

    health: mavsdk.telemetry.Health
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break

    await drone.action.arm()
    await drone.action.set_takeoff_altitude(TAKEOFF_ALTITUDE)
    await drone.action.takeoff()

    # Randomly move drone
    while True:
        pos: tuple[float, float, float] = await random_position(
            drone, DEFAULT_SPREAD_LATLON, DEFAULT_SPREAD_ALTITUDE
        )
        await drone.action.goto_location(*pos, 0.0)
        await asyncio.sleep(4.0 * random.random() * random.random())


async def print_status_text(drone: mavsdk.System) -> None:
    """
    Prints status text
    """

    try:
        status_text: mavsdk.telemetry.RcStatus
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


async def run() -> None:
    """
    Runs test code
    """

    avoiding_drone: mavsdk.System = mavsdk.System(port=50051)
    await avoiding_drone.connect(system_address="udp://:14540")

    drone_to_avoid: mavsdk.System = mavsdk.System(port=50052)
    await drone_to_avoid.connect(system_address="udp://:14541")

    drone_position_updates: AsyncIterator[list[InputPoint]] = drone_positions(drone_to_avoid)

    asyncio.ensure_future(avoiding_drone_test(avoiding_drone, drone_position_updates))
    asyncio.ensure_future(drone_to_avoid_test(drone_to_avoid))

    # Sleep forever
    # The tests won't run if we don't
    while True:
        await asyncio.sleep(60.0)
