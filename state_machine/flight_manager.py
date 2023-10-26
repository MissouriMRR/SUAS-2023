"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process
import time
from mavsdk.telemetry import FlightMode, LandedState

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


class FlightManager:
    """
    Class that manages the state machine, kill switch, and gracefully exiting the program.

    Methods
    -------
    start_manager()
        Starts the state machine and kill switch in separate processes.
    start_state_machine(drone: Drone)
        Creates and runs a state machine in the process.
    start_kill_switch(process: Process, drone: Drone)
        Creates and runs a kill switch in the process.
    kill_switch(state_machine_process: Process, drone: Drone)
        Continuously checks for whether or not the kill switch has been activated.
        Kills the state machine if the kill switch has been activated.
    graceful_exit(drone: Drone)
        Lands the drone and exits the program.
    """

    def __init__(self) -> None:
        pass

    def start_manager(self, simflag) -> None:
        """Test running the state machine in a separate process."""
        drone_obj: Drone = Drone()
        if simflag == True:
            Drone.address = "udp://:14540"
        else:
            Drone.address = "serial:///dev/ttyUSB0:921600"


        logging.info("Starting processes")
        state_machine: Process = Process(target=self.start_state_machine, args=(drone_obj,))
        kill_switch_process: Process = Process(
            target=self.start_kill_switch, args=(state_machine, drone_obj)
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
            logging.critical(
                "Keyboard interrupt detected. Killing state machine and landing drone."
            )
        finally:
            state_machine.terminate()
            asyncio.run(self.graceful_exit(drone_obj))

    def start_state_machine(self, drone: Drone) -> None:
        """Create and run a state machine in the event loop."""
        logging.info("-- Starting state machine")
        asyncio.run(StateMachine(Start(drone), drone).run())

    def start_kill_switch(self, process: Process, drone: Drone) -> None:
        """Create and run a kill switch in the event loop."""
        logging.info("-- Starting kill switch")
        asyncio.run(self.kill_switch(process, drone))

    async def kill_switch(self, state_machine_process: Process, drone: Drone) -> None:
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
                time.sleep(1)

        logging.critical("Kill switch activated. Terminating state machine.")
        state_machine_process.terminate()
        return

    async def graceful_exit(self, drone: Drone) -> None:
        """Land the drone and exit the program."""
        await drone.connect_drone()
        logging.critical("Beginning graceful exit. Landing drone...")
        await drone.system.action.return_to_launch()
        async for state in drone.system.telemetry.landed_state():
            if state == LandedState.ON_GROUND:
                logging.info("Drone landed successfully.")
                break
        logging.info("Drone landed. Exiting program...")
        return
