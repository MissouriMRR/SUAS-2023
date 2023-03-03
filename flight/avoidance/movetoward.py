"""
This module implements a function to tell the drone
to starting moving toward a location
"""

import mavsdk
import mavsdk.offboard
import mavsdk.telemetry
import utm

from .vector import Vector3
from .velocity import Velocity


async def move_toward(
    drone: mavsdk.System,
    latitude: float,
    longitude: float,
    absolute_altitude_m: float,
    time_seconds: float = 3.0,
) -> mavsdk.offboard.VelocityNedYaw:
    """
    Causes the drone to start moving toward a location;
    only sets the drone's velocity once, then returns

    Parameters
    ----------
    drone : mavsdk.System
        The drone to move
    latitude : float
        The latitude, in degrees
    longitude : float
        The longitude, in degrees
    absolute_altitude_m : float
        The altitude above mean sea level, in meters
    time_seconds : float
        Controls how quickly the drone will attempt to move
        to the target; the drone may not be able to actually
        move this quickly

    Returns
    -------
    The value the drone's velocity was set to,
    as a mavsdk.offboard.VelocityNewYaw object
    """

    # Get drone position
    drone_position: mavsdk.telemetry.Position = await anext(drone.telemetry.position())

    # Get drone and target utm positions
    target_utm: tuple[float, float, int, str] = utm.from_latlon(latitude, longitude)
    drone_utm: tuple[float, float, int, str] = utm.from_latlon(
        drone_position.latitude_deg,
        drone_position.longitude_deg,
        force_zone_number=target_utm[2],
        force_zone_letter=target_utm[3],
    )

    # Calculate difference in positions
    position_diff: Vector3 = Vector3(
        target_utm[0] - drone_utm[0],
        target_utm[1] - drone_utm[1],
        absolute_altitude_m - drone_position.absolute_altitude_m,
    )

    # Calculate target velocity based on time_seconds
    target_velocity: Vector3 = position_diff / time_seconds

    # Create Velocity object
    result: mavsdk.offboard.VelocityNedYaw = Velocity(
        target_velocity.y,  # north
        target_velocity.x,  # east
        -target_velocity.z,  # down
    ).to_mavsdk_velocitynedyaw()

    # Set drone's velocity
    await drone.offboard.set_velocity_ned(result)

    return result
