"""File to test the kill switch functionality of the state machine."""

import asyncio
import logging
from multiprocessing import Process
from mavsdk.telemetry import FlightMode

from state_machine.flight_manager import FlightManager
from state_machine.drone import Drone


async def run_flight_code() -> None:
    """Run flight code to hold the drone in mid air and log the flight mode."""
    logging.info("Starting state machine")
    drone: Drone = Drone()
    await drone.connect_drone()
    # connect to the drone
    logging.info("Waiting for drone to connect...")
    async for state in drone.system.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    logging.info("Waiting for drone to have a global position estimate...")
    async for health in drone.system.telemetry.health():
        if health.is_global_position_ok:
            logging.info("Global position estimate ok")
            break

    logging.info("-- Arming")
    await drone.system.action.arm()

    logging.info("-- Taking off")
    await drone.system.action.takeoff()

    alerted: bool = False
    async for flight_mode in drone.system.telemetry.flight_mode():
        logging.info("Flight mode: %s", flight_mode)
        if flight_mode == FlightMode.HOLD and not alerted:
            logging.info("Holding position. Test the kill switch now.")
            alerted = True
        await asyncio.sleep(1)


def start_1() -> None:
    """Start the flight code in async."""
    asyncio.run(run_flight_code())


def start_2(flight_process: Process) -> None:
    """Start the kill switch in async.

    Args:
        flight_process (Process): The process running the flight code.
    """
    flight_manager: FlightManager = FlightManager()
    flight_manager.drone.address = "udp://:14540"
    asyncio.run(FlightManager().kill_switch(flight_process))


async def start_test() -> None:
    """Start the unit test."""
    logging.basicConfig(level=logging.INFO)
    flight_manager_process: Process = Process(target=start_1)
    kill_switch_process: Process = Process(target=start_2, args=(flight_manager_process,))

    flight_manager_process.start()
    kill_switch_process.start()


if __name__ == "__main__":
    asyncio.run(start_test())
