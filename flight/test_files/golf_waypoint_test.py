"""
Main driver code for moving drone to each waypoint
"""

import asyncio
import logging
import sys

from typing import List

from mavsdk import System

# from flight.waypoint import goto

SIM_ADDR: str = "udp://:14540"
CON_ADDR: str = "serial:///dev/ttyUSB0:921600"


# Python imports made me angry so I copied move_to here
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
        before moving on to another waypoint. If its 1, it will move at normal speed,
        if its less than 1(0.83), it will be faster.
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
                (round(drone_lat, int(6 * fast_param)) == round(latitude, int(6 * fast_param)))
                and (
                    round(drone_long, int(6 * fast_param)) == round(longitude, int(6 * fast_param))
                )
                and (round(drone_alt, 1) == round(altitude_in_meters, 1))
            ):
                location_reached = True
                logging.info("arrived")
                # sleeps for 15 seconds to give substantial time for the airdrop,
                # can be changed later.
                await asyncio.sleep(3)
                break

        # tell machine to sleep to prevent contstant polling, preventing battery drain
        await asyncio.sleep(1)
    return


# duplicate code disabled for testing function
# pylint: disable=duplicate-code
async def run() -> None:
    """
    This function is a driver to test the goto function and runs through the
    given waypoints in the lats and longs lists at the altitude of 100.
    Makes the drone move to each location in the lats and longs arrays
    at the altitude of 100 and

    Notes
    -----
    Currently has 4 values in each the Lats and Longs array and code is looped
    and will stay in that loop until the drone has reached each of locations
    specified by the latitude and longitude and continues to run until forced disconnect
    """
    # Put all latitudes, longitudes and altitudes into separate arrays
    lats: List[float] = [37.948658, 37.948200, 37.948358, 37.948800]
    longs: List[float] = [-91.784431, -91.783406, -91.783253, -91.784169]

    # create a drone object
    drone: System = System()
    await drone.connect(system_address=SIM_ADDR)

    # initilize drone configurations
    await drone.action.set_takeoff_altitude(12)
    await drone.action.set_maximum_speed(20)

    # connect to the drone
    logging.info("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    logging.info("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            logging.info("Global position estimate ok")
            break

    logging.info("-- Arming")
    await drone.action.arm()

    logging.info("-- Taking off")
    await drone.action.takeoff()

    # wait for drone to take off
    await asyncio.sleep(10)

    # move to each waypoint in mission
    for i in range(6):
        logging.info("Starting loop %s", i)
        for point in range(len(lats)):
            await move_to(drone, lats[point], longs[point], 100, 0.67)

    # return home
    logging.info("Last waypoint reached")
    logging.info("Returning to home")
    await drone.action.return_to_launch()
    print("Staying connected, press Ctrl-C to exit")

    # infinite loop till forced disconnect
    while True:
        await asyncio.sleep(1)


# Runs through the code until it has looped through each element of
# the Lats and Longs array and the drone has arrived at each of them
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Program ended")
        sys.exit(0)
