"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process
import time
from mavsdk.telemetry import FlightMode, LandedState

from state_machine.flight_settings import FlightSettings
from .drone import Drone
from .state_machine import StateMachine
from .states import Start


class FlightManager:
    """
    Class that manages the state machine, kill switch, and gracefully exiting the program.

    Methods
    -------
    __init__(self) -> None
        Initialize a flight manager object.
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
        """Initialize a flight manager object."""

    def start_manager(self, simflag: bool) -> None:
        """Test running the state machine in a separate process."""
        drone_obj: Drone = Drone()
        if simflag is True:
            Drone.address = "udp://:14540"
        else:
            Drone.address = "serial:///dev/ttyUSB0:921600"
        flight_settings_obj: FlightSettings = FlightSettings()

        logging.info("Starting processes")
        state_machine: Process = Process(
            target=self.start_state_machine, args=(drone_obj, flight_settings_obj)
        )
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

    def start_state_machine(self, drone: Drone, flight_settings: FlightSettings) -> None:
        """
        Create and start a state machine in the event loop. This method should
        be called in its own process.

        Parameters
        ----------The callable object which gets executed when the `run` method is called.
        drone : Drone
            The drone the state machine will control.
        flight_settings : FlightSettings
            The flight settings to use.
        """
        logging.info("-- Starting state machine")
        asyncio.run(StateMachine(Start(drone, flight_settings), drone, flight_settings).run())

    def start_kill_switch(self, state_machine_process: Process, drone: Drone) -> None:
        """
        Create and start a kill switch in the event loop.

        Parameters
        ----------
        state_machine_process : Process
            The process running the state machine to kill.
        drone : Drone
            The drone that is controlled by the state machine.
        """
        logging.info("-- Starting kill switch")
        asyncio.run(self.kill_switch(state_machine_process, drone))

    async def kill_switch(self, state_machine_process: Process, drone: Drone) -> None:
        """
        Enable the kill switch and wait until it activates. The drone should be
        in manual mode after this method returns.

        Parameters
        ----------
        state_machine_process : Process
            The process running the state machine to kill. This process will
            be terminated.
        drone : Drone
            The drone that is controlled by the state machine.
        """

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

    async def graceful_exit(self, drone: Drone) -> None:
        """
        Land the drone and exit the program.

        Parameters
        ----------
        drone : Drone
            The drone to land.
        """

        await drone.connect_drone()
        logging.critical("Beginning graceful exit. Landing drone...")
        await drone.system.action.return_to_launch()
        async for state in drone.system.telemetry.landed_state():
            if state == LandedState.ON_GROUND:
                logging.info("Drone landed successfully.")
                break
        logging.info("Drone landed. Exiting program...")
