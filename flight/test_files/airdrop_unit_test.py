"""
File for the airdrop unit test
"""

import asyncio
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

    flight_settings: FlightSettings = FlightSettings()

    logging.info("Starting processes")
    state_machine: Process = Process(
        target=asyncio.run(
            StateMachine(Airdrop(drone, flight_settings), drone, flight_settings).run()
        )
    )

    state_machine.start()

    try:
        state_machine.join()
        logging.info("State machine joined")

        logging.info("Done!")
    except KeyboardInterrupt:
        logging.critical("Keyboard interrupt detected. Killing state machine and landing drone.")
    finally:
        state_machine.terminate()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        print("Program ended")
        sys.exit(0)
