"""
File for test way point path for SUAS 3 miles in length
"""

import asyncio
import logging
import sys

from typing import List

from mavsdk import System


SIM_ADDR: str = "udp://:14540"
CON_ADDR: str = "serial:///dev/ttyUSB0:921600"


async def move_to(
    drone: System, latitude: float, longitude: float, altitude: float, fast_param: float
) -> None:
    """
    This function takes in a latitude, longitude and altitude and autonomously
    moves the drone to that waypoint.

    Parameters
    ----------
    drone: System
        a drone object that has all offboard data needed for computation
    latitude: float
        a float containing the requested latitude to move to
    longitude: float
        a float containing the requested longitude to move to
    altitude: float
        a float contatining the requested altitude to go to in meters
    fast_param: float
        a float that determines if the drone will take less time checking its precise location
        before moving on to another waypoint. If its 1, it will move at normal speed,
        if its less than 1(0.83), it will be faster.
    """

    # get current altitude
    async for terrain_info in drone.telemetry.home():
        absolute_altitude: float = terrain_info.absolute_altitude_m
        break

    await drone.action.goto_location(latitude, longitude, altitude + absolute_altitude, 0)
    location_reached: bool = False
    # First determine if we need to move fast through waypoints or need to slow down at each one
    # Then loops until the waypoint is reached
    while not location_reached:
        logging.info("Going to waypoint")
        print("Going to waypoint")
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
                and (round(drone_alt, 1) == round(altitude, 1))
            ):
                location_reached = True
                logging.info("arrived")
                print("arrived")
                break

        # tell machine to sleep to prevent constant polling, preventing battery drain
        await asyncio.sleep(1)
    return


async def run() -> None:
    """
    run simple waypoint flight path
    """

    # create a drone object
    drone: System = System()
    await drone.connect(system_address=SIM_ADDR)

    # initilize drone configurations
    await drone.action.set_takeoff_altitude(12)
    await drone.action.set_maximum_speed(30)

    # connect to the drone
    logging.info("Waiting for drone to connect...")
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            print("Drone discovered")
            break

    logging.info("Waiting for drone to have a global position estimate...")
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            logging.info("Global position estimate ok")
            print("Global position estimate ok")
            break

    logging.info("-- Arming")
    print("-- Arming")
    await drone.action.arm()

    logging.info("-- Taking off")
    print("-- Taking off")
    await drone.action.takeoff()

    # wait for drone to take off
    await asyncio.sleep(60)

    accuracy_mod: float = 0.83
    obj_altitude: float = 12
    points: List[List[float]] = [
        [38.31413, -76.54352],
        [38.31629, -76.55587],
        [38.31611, -76.55126],
        [38.31712, -76.55102],
        [38.31560, -76.54838],
        [38.31413, -76.54352],
        [38.31629, -76.55587],
        [38.31413, -76.54352],
        [38.31466, -76.54665],
    ]

    await move_to(drone, points[0][0], points[0][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[1][0], points[1][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[2][0], points[2][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[3][0], points[3][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[4][0], points[4][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[5][0], points[5][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[6][0], points[6][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[7][0], points[7][1], obj_altitude, accuracy_mod)

    await move_to(drone, points[8][0], points[8][1], obj_altitude, accuracy_mod)

    # return home
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
