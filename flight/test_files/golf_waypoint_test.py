"""
Main driver code for moving drone to each waypoint
"""

import asyncio
import logging
import sys

from typing import List

from mavsdk import System

from flight.waypoint import goto

SIM_ADDR: str = "udp://:14540"
CON_ADDR: str = "serial:///dev/ttyUSB0:921600"


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
    # Put all latitudes, longitudes and altitudes into seperate arrays
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
    for point in range(len(lats)):
        await goto.move_to(drone, lats[point], longs[point], 100, True)

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
