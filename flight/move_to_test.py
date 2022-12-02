"""
Main driver code for moving drone to each waypoint
"""

import asyncio
from mavsdk import System
import logging
import sys

import flight.extract_gps
import flight.Waypoint.goto


async def run() -> None:
    """
    This function is a driver to test the goto function and runs through the
    given waypoints in the lats and longs lists at the altitude of 100.
    Makes the drone move to each location in the lats and longs arrays at the altitude of 100.

    Notes
    -----
    Currently has 3 values in each the Lats and Longs array and code is looped and will stay in that loop
    until the drone has reached each of locations specified by the latitude and longitude and
    continues to run until forced disconnect
    """
    # Defining file path constant for extract_gps
    PATH: str = "./data/waypoint_data.json"
    # Defining system address
    SYSTEM_ADDRESS: str = "udp://:14540"
    # Defining altitude and speed
    ALTITUDE: int = 12
    SPEED: int = 20
    # Defining fast_param constant
    FAST_PARAM: float = 0.83

    # Put all latitudes, longitudes and altitudes into seperate arrays
    lats: list[float] = []
    longs: list[float] = []
    altitudes: list[float] = []

<<<<<<< HEAD
    waypoint_data = extract_gps.extract_gps(PATH)
    waypoints = waypoint_data['waypoints']
    #waypoint: tuple
    
    waypoint: tuple
    for waypoint in waypoints:
        lats.append(waypoint.latitude)
        longs.append(waypoint.longitude)
        altitudes.append(waypoint.altitude)
        
=======
    waypoint_data = extract_gps.extract_gps("./data/waypoint_data.json")
    waypoints = waypoint_data["waypoints"]
    for i in waypoints:
        lats.append(i.latitude)
        longs.append(i.longitude)
        altitudes.append(i.altitude)
    # print(lats)
    # print(longs)
    # print(altitudes)
>>>>>>> be1e82ccb2c5e601fe97288c48039e170f0708a5
    # create a drone object
    drone: System = System()
    await drone.connect(SYSTEM_ADDRESS)

    # initilize drone configurations
    await drone.action.set_takeoff_altitude(ALTITUDE)
    await drone.action.set_maximum_speed(SPEED)

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
    point: int
    for point in range(len(lats)):
        await goto.move_to(drone, lats[point], longs[point], 100, FAST_PARAM)

    # return home
    logging.info("Last waypoint reached")
    logging.info("Returning to home")
    await drone.action.return_to_launch()
    print("Staying connected, press Ctrl-C to exit")

    # infinite loop till forced disconnect
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    """
    Runs through the code until it has looped through each element of
    the Lats and Longs array and the drone has arrived at each of them
    """
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
<<<<<<< HEAD
        logging.info("CTRL+C: Program ended")
        sys.exit(0)
=======
        print("Program ended")
        sys.exit(0)
>>>>>>> be1e82ccb2c5e601fe97288c48039e170f0708a5
