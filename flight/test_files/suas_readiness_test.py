"""
Main driver code for moving drone to each waypoint
"""

import asyncio
import logging
import sys

from mavsdk import System

# sys.path.append("././SUAS-2023/flight")
# from flight.waypoint.goto import move_to

SIM_ADDR: str = "udp://:14540"
CON_ADDR: str = "serial:///dev/ttyUSB0:921600"


# Python imports made me angry so I just copied move_to here
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
                await asyncio.sleep(1)
                break

        # tell machine to sleep to prevent contstant polling, preventing battery drain
        await asyncio.sleep(1)
    return


# duplicate code disabled for testing function
# pylint: disable=duplicate-code
async def run() -> None:
    """
    Runs
    """

    lats: list[float] = [37.94893290, 37.947899284]
    longs: list[float] = [-91.784668343, -91.782420970]
    # rando_waypoint: tuple[float, float] = ()
    # create a drone object
    drone: System = System()
    await drone.connect(system_address=SIM_ADDR)

    # initilize drone configurations
    await drone.action.set_takeoff_altitude(25)
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

    print("Fetching amsl altitude at home location....")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        break

    logging.info("-- Arming")
    await drone.action.arm()

    logging.info("-- Taking off")
    print("Taking off")
    await drone.action.takeoff()

    # wait for drone to take off
    await asyncio.sleep(15)

    # Fly to first waypoint
    print("Going to first waypoint")
    await drone.action.goto_location(lats[0], longs[0], 25 + absolute_altitude, 0)
    await asyncio.sleep(5)
    print("Reached first waypoint")

    # Begin 12 mile flight
    print("Starting the line")
    for i in range(43):
        point: int
        for point in range(len(lats)):
            await move_to(drone, lats[point], longs[point], 75, 0.5)
            print("Reached waypoint")
        print("Iteration:", i)

    # return home
    logging.info("12 miles accomplished")
    logging.info("Returning to home")
    await drone.action.return_to_launch()
    print("Returned to launch")
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
