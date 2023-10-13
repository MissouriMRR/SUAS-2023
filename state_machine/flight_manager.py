"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process
import time
from mavsdk.telemetry import FlightMode, LandedState

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


def start_processes() -> None:
    """Test running the state machine in a separate process."""
    drone_obj: Drone = Drone()

    logging.info("Starting processes")
    state_machine: Process = Process(target=start_state_machine, args=(drone_obj,))
    kill_switch_process: Process = Process(
        target=start_kill_switch, args=(state_machine, drone_obj)
    )

    state_machine.start()
    kill_switch_process.start()

    try:
        state_machine.join()
        logging.info("State machine joined")
        kill_switch_process.join()
        logging.info("Kill switch joined")

        logging.info("Done!")
    except KeyboardInterrupt:
        logging.critical("Keyboard interrupt detected. Killing state machine and landing drone.")
        state_machine.terminate()
        graceful: Process = Process(target=start_graceful_exit, args=(drone_obj,))
        graceful.start()
        graceful.join()
        return


def start_state_machine(drone: Drone) -> None:
    """Create and run a state machine in the event loop."""
    print("Running drone")
    asyncio.run(StateMachine(Start(drone), drone).run())


def start_kill_switch(process: Process, drone: Drone) -> None:
    asyncio.run(kill_switch(process, drone))


async def kill_switch(state_machine_process: Process, drone: Drone) -> None:
    """
    Continuously check for whether or not the kill switch has been activated.
    """

    # connect to the drone
    logging.debug("Kill switch running")
    logging.info("Waiting for drone to connect...")
    await drone.connect_drone()
    async for state in drone.system.core.connection_state():
        if state.is_connected:
            logging.info("Kill switch has been enabled.")
            break

    async for flight_mode in drone.system.telemetry.flight_mode():
        while flight_mode != FlightMode.MANUAL:
            logging.info(flight_mode)
            time.sleep(1)

    logging.critical("Kill switch activated. Terminating state machine.")
    state_machine_process.terminate()


def start_graceful_exit(drone: Drone) -> None:
    """Start the graceful exit process."""
    asyncio.run(graceful_exit(drone))


async def graceful_exit(drone: Drone) -> None:
    """Land the drone and exit the program."""
    await drone.connect_drone()
    logging.critical("Ctrl-C detected. Landing drone...")
    await drone.system.action.return_to_launch()
    async for state in drone.system.telemetry.landed_state():
        if state == LandedState.ON_GROUND:
            logging.info("Drone landed successfully.")
            break
    logging.info("Drone landed. Exiting program...")
    raise SystemExit(1)
