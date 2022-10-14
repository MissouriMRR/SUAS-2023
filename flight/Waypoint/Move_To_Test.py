"""
Main driver code for moving drone to each waypoint
"""

import asyncio
import json
import argparse
import goto
from mavsdk import System
import mavsdk as sdk
import logging
import math
import typing
from typing import Dict, List
import sys


async def run() -> None:
    """
    This function is just a driver to test the goto function and runs through the
    entire waypoint section of the SUAS competition
    """
    # Put all latitudes, longitudes and altitudes into seperate arrays
    lats: List[float] = [37.9008502, 37.9008129, 37.8964543]
    longs: List[float] = [-91.6615228, -91.6615335, -91.6570381]
    altitudes: List[float] = [100, 100, 100]
    # waypoints: List[Dict[str,float]] =json.load("numbers.json")
    # for i in waypoints:
    # for key,val in i.items():
    # if(key=="latitude"):
    #      lats.append(val)
    # if(key=="longitude"):
    # longs.append(val)
    # if(key=="altitude"):
    #   altitudes.append(val)

    # create a drone object
    drone: System = System()
    await drone.connect(system_address="udp://:14540")

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
        await goto.move_to(drone, lats[point], longs[point], altitudes[point], True)

    # return home
    logging.info("Last waypoint reached")
    logging.info("Returning to home")
    await drone.action.return_to_launch()
    print("Staying connected, press Ctrl-C to exit")

    # infinite loop till forced disconnect
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    # Main driver of drone
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Program ended")
        sys.exit(0)
