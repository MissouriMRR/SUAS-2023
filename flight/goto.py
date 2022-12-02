"""
File containing the move_to function responsible
for moving the drone to a certain waypoint and stopping there for 15 secs
"""

import asyncio
from mavsdk import System
import logging


async def move_to(
    drone: System, latitude: float, longitude: float, altitude: float, fast_param: float
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
    fast_param: float
        a float that determines if the drone will take less time checking its precise location
        before moving on to another waypoint. If its 1, it will move at normal speed, if its less than 1(0.83),
        it will be faster.
    """

    # converts feet into meters
    altitude_in_meters = altitude * 0.3048

    # get current altitude
    async for terrain_info in drone.telemetry.home():
        absolute_altitude: float = terrain_info.absolute_altitude_m
        break

    await drone.action.goto_location(latitude, longitude, altitude_in_meters + absolute_altitude, 0)
    location_reached: bool = False
    # First determine if we need to move fast through waypoints or need to slow down at each one
    # Then loops until the waypoint is reached
    while not location_reached:
        logging.info("Going to waypoint")
        async for position in drone.telemetry.position():
            # continuously checks current latitude, longitude and altitude of the drone
            drone_lat: float = position.latitude_deg
            drone_long: float = position.longitude_deg
            drone_alt: float = position.relative_altitude_m

            #  accurately checks if location is reached and stops for 15 secs and then moves on.
            if (
                (round(drone_lat, int(6*fast_param)) == round(latitude, int(6*fast_param)))
                and (round(drone_long, int(6*fast_param)) == round(longitude, int(6*fast_param)))
                and (round(drone_alt, 1) == round(altitude_in_meters, 1))
            ):
                location_reached = True
                logging.info("arrived")
                # sleeps for 15 seconds to give substantial time for the airdrop, can be changed later.
                await asyncio.sleep(15)
                break

        # tell machine to sleep to prevent contstant polling, preventing battery drain
        await asyncio.sleep(1)
    return
