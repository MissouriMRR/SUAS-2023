"""
File for the airdrop unit test
"""

import asyncio
import json
import logging
import sys
from multiprocessing import Process
from mavsdk import System

from state_machine.flight_settings import FlightSettings
from state_machine.state_machine import StateMachine
from state_machine.states import Airdrop


async def run() -> None:
    """
    Runs the Airdrop unit test
    """
    # create a drone object
    drone: System = System()
    await drone.connect(system_address="udp://:14540")

    await prep(drone)

    print("I know it got heresies")

    flight_settings: FlightSettings = FlightSettings()

    logging.info("Starting processes")
    print("I got here")
    state_machine: Process = Process(
        target=airdrop_run,
        args=(drone, flight_settings,)
    )

    print("I also got here")
    state_machine.start()

    try:
        print("maybe here")
        state_machine.join()
        logging.info("State machine joined")
        print("perhapsies here")

        drop_loc = 1

        with open("flight/data/output.json", encoding="utf8") as output:
            bottle_locations = json.load(output)

        location_reached: bool = False

        while not location_reached:
            logging.info("Going to waypoint")
            print(f"Going to waypoint {str(drop_loc)}")
            while drop_loc < 5:
                bottle_loc: dict[str, float] = bottle_locations[str(drop_loc)]
                async for position in drone.telemetry.position():
                    # continuously checks current latitude, longitude and altitude of the drone
                    drone_lat: float = position.latitude_deg
                    drone_long: float = position.longitude_deg
                    drone_alt: float = position.relative_altitude_m
                    latitude: float = bottle_loc["latitude"]
                    longitude: float = bottle_loc["longitude"]
                    altitude: float = 75

                    #  accurately checks if location is reached and stops for 15 secs
                    # and then moves on.
                    if (
                        (round(drone_lat, int(5)) == round(latitude, int(5)))
                        and (round(drone_long, int(5)) == round(longitude, int(5)))
                        and (round(drone_alt, 1) == round(altitude, 1))
                    ):
                        location_reached = True
                        logging.info("arrived")
                        break
                drop_loc = drop_loc + 1

            # tell machine to sleep to prevent constant polling, preventing battery drain
            await asyncio.sleep(1)

        logging.info("Done!")
    except KeyboardInterrupt:
        logging.critical("Keyboard interrupt detected. Killing state machine and landing drone.")
    finally:
        state_machine.terminate()

def airdrop_run(drone: System, flight_settings: FlightSettings) -> None:
    asyncio.run(
        StateMachine(Airdrop(drone, flight_settings), drone, flight_settings).run()
    )

async def prep(drone: System) -> None:
    """
    A little prep for the unit test
    Parameters
    ----------
    drone:System
        the drone object
    """

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



