"""
Test code for our drone in obstacle avoidance
"""

import asyncio
import random
from typing import AsyncIterator

import mavsdk
import mavsdk.core
import mavsdk.offboard
import mavsdk.telemetry
import utm

from .avoidance_goto import goto_with_avoidance
from .movement import goto_location_offboard
from .point import InputPoint, Point

TAKEOFF_ALTITUDE: float = 40.0


async def takeoff(drone: mavsdk.System, altitude: float) -> None:
    """
    Makes a drone take off and waits until it reaches the desired altitude

    Parameters
    ----------
    drone : mavsdk.System
        The drone that will take off
    altitude : float
        The minimum altitude, in meters, above the ground to take off to;
        the actual altitude might be slightly higher
    """

    await drone.action.set_takeoff_altitude(altitude + 2.0)
    await drone.action.takeoff()

    # Temporary solution
    # Originally attempted to use telemetry to detect when the desired
    #   altitude was reached, but telemetry is broken when taking off
    await asyncio.sleep(30.0)


async def random_position(
    drone: mavsdk.System, spread_horizontal: float = 15.0, spread_vertical: float = 10.0
) -> tuple[float, float, float]:
    """
    Generates a random position relative to a drone's current position

    Parameters
    ----------
    drone : mavsdk.System
        The drone to generate a random position relative to
    spread_horizontal : float = 15.0
        The spread, in meters, from the drone's north and east
        positions in which new, random north and east positions
        will be generated
    spread_vertical : float = 10.0
        The spread, in meters, from the drone's altitude
        in which a new, random altitude will be generated

    Returns
    -------
    A random, uniformly distributed position relative to the drone's position
    latitude : float
        Same as mavsdk.telemetry.Position.latitude_deg
    longitude : float
        Same as mavsdk.telemetry.Position.longitude_deg
    altitude : float
        Same as mavsdk.telemetry.Position.absolute_altitude_m
    """

    # Get the drone's position
    position: mavsdk.telemetry.Position = await anext(drone.telemetry.position())

    # Convert latitude and longitude to UTM
    utm_easting: float
    utm_northing: float
    utm_zone_number: int
    utm_zone_letter: str
    utm_easting, utm_northing, utm_zone_number, utm_zone_letter = utm.from_latlon(
        position.latitude_deg, position.longitude_deg
    )

    # Randomly change UTM coordinates
    utm_easting += 2 * spread_horizontal * (random.random() - 0.5)
    utm_northing += 2 * spread_horizontal * (random.random() - 0.5)

    # Randomly change altitude
    altitude: float = position.absolute_altitude_m + 2 * spread_vertical * (random.random() - 0.5)

    # Convert back to latitude and longitude
    latitude: float
    longitude: float
    latitude, longitude = utm.to_latlon(utm_easting, utm_northing, utm_zone_number, utm_zone_letter)

    return latitude, longitude, altitude


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
        in_point: InputPoint = point.as_typed_dict()

        if len(positions) > 4:
            positions = positions[1:]

        positions.append(in_point)

        yield positions[:]
        await asyncio.sleep(1.0)


async def avoiding_drone_test(
    drone: mavsdk.System, position_updates: AsyncIterator[list[InputPoint]]
) -> None:
    """
    Runs test code for the drone trying to avoid the other drone

    Parameters
    ----------
    drone : mavsdk.System
        The drone this test will control
    position_updates : AsyncIterator[list[InputPoint]]
        Position updates for the drone this drone should avoid
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
    await takeoff(drone, TAKEOFF_ALTITUDE)
    await drone.offboard.set_velocity_ned(mavsdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.offboard.start()

    await goto_location_offboard(drone, 10.0, 10.0, 10.0, None)

    # Randomly move drone
    while True:
        pos: tuple[float, float, float] = await random_position(drone)
        await goto_with_avoidance(drone, *pos, None, position_updates)
        await asyncio.sleep(4.0 * random.random() * random.random())


async def drone_to_avoid_test(drone: mavsdk.System) -> None:
    """
    Runs test code for the drone which the other drone should avoid

    Parameters
    ----------
    drone : mavsdk.System
        The drone this test will control
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
    await takeoff(drone, TAKEOFF_ALTITUDE)
    await drone.offboard.set_velocity_ned(mavsdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.offboard.start()

    # Randomly move drone
    while True:
        pos: tuple[float, float, float] = await random_position(drone)
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
