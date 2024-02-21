"""
File for the airdrop unit test
"""

import asyncio
import logging
from mavsdk import System

from state_machine.flight_settings import FlightSettings
from state_machine.state_machine import StateMachine
from state_machine.states import Airdrop
from state_machine.drone import Drone


async def run() -> None:
    """
    Runs the Airdrop unit test
    """

    logging.info("Creating the drone")
    drone: Drone = Drone()
    # create a drone object
    await drone.connect_drone()

    await prep(drone.system)

    flight_settings: FlightSettings = FlightSettings()

    logging.info("starting airdrop")

    await airdrop_run(drone, flight_settings)

    try:
        # tell machine to sleep to prevent constant polling, preventing battery drain
        await asyncio.sleep(1)

        logging.info("Done!")
    except KeyboardInterrupt:
        logging.critical("Keyboard interrupt detected. Killing state machine and landing drone.")
    finally:
        print("Done")


async def airdrop_run(drone: Drone, flight_settings: FlightSettings) -> None:
    """
    Starts airdrop state of statemachine

    Parameters
    ----------
    drone: Drone
        drone class that includes drone object

    flight_settings: FlightSettings
        settings for flight to be passed into the statemachine
    """
    drone.odlc_scan = False
    await StateMachine(Airdrop(drone, flight_settings), drone, flight_settings).run()


async def prep(drone: System) -> None:
    """
    A little prep for the unit test

    Parameters
    ----------
    drone:System
        the drone object
    """

    logging.info("prepping the drone")

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
