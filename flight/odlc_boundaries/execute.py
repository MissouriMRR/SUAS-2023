"""
File containing the move_to function responsible
for moving the drone to a certain waypoint
"""

import asyncio
from mavsdk import System
import logging


async def move_to(
    drone: System, latitude: float, longitude: float, altitude: float, fast_mode: bool
) -> None:
    """
    This function takes in a latitude, longitude and altitude and autonomously
    moves the drone to that waypoint. This function will also auto convert the altitude
    from feet to meters.

    Parameters
    ----------
    drone: System
        a drone object that has all offboard data needed for computation
    latitude: float
        a float containing the requested latitude to move to
    longitude: float
        a float containing the requested longitude to move to
    altitude: float
        a float contatining the requested altitude to go to (in feet)
    fast_mode: bool
        a boolean that determines if the drone will take less time checking its precise location
        before moving on to another waypoint. If its true, it will move faster, if it is false,
        it will move at normal speed
    """

    # converts feet into meters
    altitudeinMeters: float = altitude * 0.3048

    # get current altitude
    async for terrain_info in drone.telemetry.home():
        absolute_altitude: float = terrain_info.absolute_altitude_m
        break

    await drone.action.goto_location(latitude, longitude, altitudeinMeters + absolute_altitude, 0)
    location_reached: bool = False
    # First determine if we need to move fast through waypoints or need to slow down at each one
    # Then loops until the waypoint is reached
    if fast_mode == True:
        while not location_reached:
            logging.info("Going to waypoint")
            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

                # roughly checks if location is reached and moves on if so
                if (
                    (round(drone_lat, 3) == round(latitude, 3))
                    and (round(drone_long, 3) == round(longitude, 3))
                    and (round(drone_alt, 1) == round(altitude, 1))
                ):
                    location_reached = True
                    logging.info("arrived")
                    break

            # tell machine to sleep to prevent contstant polling, preventing battery drain
            await asyncio.sleep(1)
            # tell machine to sleep to prevent contstant polling, preventing battery drain
            await asyncio.sleep(1)
    return
