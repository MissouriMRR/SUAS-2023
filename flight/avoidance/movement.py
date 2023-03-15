"""
Implements drone movement functions using offboard commands
"""

import asyncio
import math

import mavsdk
import mavsdk.offboard
import mavsdk.telemetry
import utm

from .vector import Vector3


async def _difference_vector(
    drone: mavsdk.System,
    latitude_deg: float,
    longitude_deg: float,
    absolute_altitude_m: float,
) -> Vector3:
    """
    Calculates the difference in position between
    a given coordinate and a drone

    Parameters
    ----------
    drone : mavsdk.System
        The drone
    latitude_deg : float
        The latitude_deg, in degrees, of the coordinate
    longitude_deg : float
        The longitude_deg, in degrees, of the coordinate
    absolute_altitude_m : float
        The altitude, in meters above mean sea level,
        of the coordinate

    Returns
    -------
    A Vector3 object representing the difference in position
    between the given coordinate and the drone
    """

    # Get drone position
    drone_position: mavsdk.telemetry.Position = await anext(drone.telemetry.position())

    # Get drone and target utm positions
    # UTM tuples are easting, northing, zone number, zone letter
    target_utm: tuple[float, float, int, str] = utm.from_latlon(latitude_deg, longitude_deg)
    drone_utm: tuple[float, float, int, str] = utm.from_latlon(
        drone_position.latitude_deg,
        drone_position.longitude_deg,
        force_zone_number=target_utm[2],
        force_zone_letter=target_utm[3],
    )

    # Return difference in position
    return Vector3(
        target_utm[1] - drone_utm[1],  # northing
        target_utm[0] - drone_utm[0],  # easting
        drone_position.absolute_altitude_m - absolute_altitude_m,  # reversed because down
    )


async def move_toward(
    drone: mavsdk.System,
    latitude_deg: float,
    longitude_deg: float,
    absolute_altitude_m: float,
    yaw_deg: float | None = None,
    time_seconds: float = 1.0,
) -> mavsdk.offboard.VelocityNedYaw:
    """
    Causes the drone to start moving toward a location;
    only sets the drone's velocity once, then returns

    Parameters
    ----------
    drone : mavsdk.System
        The drone to move
    latitude_deg : float
        The latitude_deg, in degrees, to move toward
    longitude_deg : float
        The longitude_deg, in degrees, to move toward
    absolute_altitude_m : float
        The altitude above mean sea level, in meters
    yaw_deg : float | None = None
        The yaw, in degrees, to use when moving; north is 0 degrees,
        with yaw increasing clockwise looking down; this value will be
        calculated from the north and east components of the difference
        vector between the target position and the drone if not provided
    time_seconds : float = 1.0
        Controls how quickly the drone will attempt to move
        to the target; the drone may not be able to actually
        move this quickly

    Returns
    -------
    The value the drone's velocity was set to,
    as a mavsdk.offboard.VelocityNedYaw object
    """

    # Get difference in position between target and drone
    position_diff: Vector3 = await _difference_vector(
        drone, latitude_deg, longitude_deg, absolute_altitude_m
    )

    # Calculate target velocity based on time_seconds
    target_velocity: Vector3 = position_diff / time_seconds

    # Create VelocityNedYaw object
    result: mavsdk.offboard.VelocityNedYaw = target_velocity.to_mavsdk_velocitynedyaw(yaw_deg)

    # Set drone's velocity
    await drone.offboard.set_velocity_ned(result)

    return result


async def goto_location_offboard(
    drone: mavsdk.System,
    latitude_deg: float,
    longitude_deg: float,
    absolute_altitude_m: float,
    yaw_deg: float | None = None,
    stop_radius: float = 1.0,
) -> None:
    """
    Causes the drone to go to a location using offboard commands;
    importantly, this coroutine can be canceled

    Parameters
    ----------
    drone : mavsdk.System
        The drone to move
    latitude_deg : float
        The latitude, in degrees, to go to
    longitude_deg : float
        The longitude, in degrees, to go to
    absolute_altitude_m : float
        The altitude above mean sea level, in meters
    yaw_deg : float | None = None
        The yaw, in degrees, to use when moving; north is 0 degrees,
        with yaw increasing clockwise looking down; this value will be
        calculated from the north and east components of the difference
        vector between the target position and the drone if not provided
    stop_radius : float = 1.0
        Controls how close the drone must be, in meters,
        to the target before stopping
    """

    position_diff: Vector3

    if yaw_deg is None:
        position_diff = await _difference_vector(
            drone, latitude_deg, longitude_deg, absolute_altitude_m
        )
        yaw_deg = math.degrees(math.atan2(position_diff.east, position_diff.north))

    try:
        while True:
            # Get difference in position between target and drone
            position_diff = await _difference_vector(
                drone, latitude_deg, longitude_deg, absolute_altitude_m
            )

            if position_diff.length < stop_radius:
                return

            await move_toward(drone, latitude_deg, longitude_deg, absolute_altitude_m, yaw_deg)
            await asyncio.sleep(0.25)
    finally:
        # Set velocity to 0 but don't change yaw
        await drone.offboard.set_velocity_ned(
            mavsdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, yaw_deg)
        )
