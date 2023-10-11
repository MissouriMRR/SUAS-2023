"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process
import time
from mavsdk.telemetry import FlightMode

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


async def actually_run_drone(drone: Drone) -> None:
    """Create and run a state machine machine for the drone."""
    print("testing")
    await StateMachine(Start(drone), drone).run()


def run_drone(drone: Drone) -> None:
    """Create and run a state machine in the event loop."""
    print("Running drone")
    asyncio.run(actually_run_drone(drone))


def process_test() -> None:
    """Test running the state machine in a@@ separate process."""
    drone_obj: Drone = Drone()

    print("Starting processes")
    state_machine: Process = Process(target=run_drone, args=(drone_obj,))
    kill_switch_process: Process = Process(
        target=start_kill_switch, args=(state_machine, drone_obj)
    )

    state_machine.start()
    kill_switch_process.start()

    state_machine.join()
    print("State machine joined")
    kill_switch_process.join()
    print("Kill switch joined")

    print("Done!")


def start_kill_switch(process: Process, drone: Drone) -> None:
    """Start the kill switch task"""
    asyncio.ensure_future(kill_switch(process, drone))


async def kill_switch(state_machine_process: Process, drone: Drone) -> None:
    """
    Continuously check for whether or not the kill switch has been activated
    """

    # connect to the drone
    logging.info("Waiting for drone to connect...")
    async for state in drone.system.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    while drone.system.telemetry.flight_mode() != FlightMode.MANUAL:
        print(drone.system.telemetry.flight_mode())
        time.sleep(1)
    state_machine_process.terminate()
