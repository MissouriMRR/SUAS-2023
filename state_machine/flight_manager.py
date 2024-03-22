"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process
import sys
import time
from typing import Any, Dict
from mavsdk.telemetry import FlightMode, LandedState

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import Start
from state_machine.states.state import State
from state_machine.flight_settings import FlightSettings
from state_machine.state_tracker import read_state_data


class FlightManager:
    """
    Class that manages the state machine, kill switch, and gracefully exiting the program.

    Methods
    -------
    __init__(self) -> None
        Initialize a flight manager object.
    run_manager() -> Awaitable[None]
        Run the state machine until completion in a separate process.
        Sets the drone address to the simulation or physical address.
    _run_state_machine(drone: Drone) -> None
        Create and run a state machine until completion in the event loop.
        This method should be called in its own process.
    _run_kill_switch(state_machine_process: Process, drone: Drone) -> None
        Create and run a kill switch in the event loop.
    _kill_switch(state_machine_process: Process, drone: Drone) -> Awaitable[None]
        Enable the kill switch and wait until it activates. The drone should be
        in manual mode after this method returns.
    _graceful_exit(drone: Drone) -> Awaitable[None]
        Lands the drone and exits the program.
    """

    def __init__(self) -> None:
        self.drone: Drone = Drone()

    async def run_manager(
        self, sim_flag: bool, path_data_path: str = "flight/data/waypoint_data.json"
    ) -> None:
        """
        Run the state machine until completion in a separate process.
        Sets the drone address to the simulation or physical address.

        Parameters
        ----------
        sim_flag : bool
            A flag representing if the drone is a simulation.
        path_data_path : str, default "flight/data/waypoint_data.json"
            The path to the JSON file containing the boundary and waypoint data.
        """
        if sim_flag:
            self.drone.address = "udp://:14540"
        else:
            self.drone.address = "serial:///dev/ttyUSB0:921600"

        flight_settings_obj: FlightSettings = FlightSettings(
            sim_flag=sim_flag, path_data_path=path_data_path
        )

        logging.info("Starting processes")
        state_machine_process: Process = Process(
            target=self._run_state_machine,
            args=(flight_settings_obj,),
        )

        self._run_kill_switch(state_machine_process)

        state_machine_process.start()

        await self._run_kill_switch(state_machine_process)

        try:
            while state_machine_process.is_alive():
                await asyncio.sleep(0.25)

            logging.info("State machine joined")

            logging.info("Done!")
        except KeyboardInterrupt:
            logging.critical(
                "Keyboard interrupt detected. Killing state machine and landing drone."
            )
        finally:
            state_machine_process.terminate()
            await self._graceful_exit()

    def _run_state_machine(self, flight_settings: FlightSettings) -> None:
        """
        Create and run a state machine until completion in the event loop.
        This method should be called in its own process.

        Parameters
        ----------
        flight_settings: FlightSettings
            The flight settings to use.
        """
        logging.info("-- Starting state machine")
        asyncio.run(
            StateMachine(Start(self.drone, flight_settings), self.drone, flight_settings).run()
        )

    async def _run_kill_switch(self, process: Process) -> None:
        """
        Create and run a kill switch in the event loop.

        Parameters
        ----------
        state_machine_process : Process
            The process running the state machine to kill.
        """
        logging.info("-- Starting kill switch")
        await self._kill_switch(process)

    async def _kill_switch(self, state_machine_process: Process) -> None:
        """
        Enable the kill switch and wait until it activates. The drone should be
        Continuously check for whether or not the kill switch has been activated.
        in manual mode after this method returns.

        Parameters
        ----------
        state_machine_process: Process
            The process running the state machine to kill. This process will
            be terminated.
        """

        # connect to the drone
        logging.debug("Kill switch running")
        logging.info("Waiting for drone to connect...")
        await self.drone.connect_drone()
        async for connection_state in self.drone.system.core.connection_state():
            if connection_state.is_connected:
                logging.info("Kill switch has been enabled.")
                break

        # async for flight_mode in self.drone.system.telemetry.flight_mode():
        #    while flight_mode != FlightMode.POSCTL:
        #        time.sleep(1)
        time.sleep(20)

        logging.critical("Kill switch activated. Terminating state machine.")

        await self.drone.system.offboard.stop()

        state_machine_process.terminate()

        # Get latest state started in the state machine
        last_state_data: Dict[str, Any] | None = read_state_data()
        if last_state_data is not None:
            logging.info(last_state_data)
            last_flight_settings: FlightSettings = FlightSettings(
                simple_takeoff=last_state_data["flight_settings"]["simple_takeoff"],
                title=last_state_data["flight_settings"]["title"],
                description=last_state_data["flight_settings"]["description"],
                waypoints=last_state_data["flight_settings"]["waypoint_count"],
                sim_flag=last_state_data["flight_settings"]["sim_flag"],
                path_data_path=last_state_data["flight_settings"]["path_data_path"],
            )
            last_drone: Drone = Drone(
                address=last_state_data["drone"]["address"],
            )
            last_drone.odlc_scan = last_state_data["drone"]["odlc_scan"]
            # in case the drone eventually needs to start from another state
            # state: State = getattr(sys.modules["state_machine.states"], last_state_data["state"])
            state = Start(last_drone, last_flight_settings)
        else:
            # Unknown last state, just use Start
            last_flight_settings = FlightSettings()
            last_drone = Drone()
            state = Start(last_drone, last_flight_settings)
        print(__name__)
        print(state)

        # Gotta wait for user input here
        logging.critical("Press enter to restart the state machine.")
        input()
        logging.critical("Are you sure?")
        input()
        state_machine: Process = Process(
            target=self._run_state_machine,
            args=(FlightSettings(),),
        )
        state_machine.start()
        await self._kill_switch(state_machine)

    async def _graceful_exit(self) -> None:
        """
        Land the drone and exit the program.
        """
        await self.drone.connect_drone()
        logging.critical("Beginning graceful exit. Landing drone...")
        await self.drone.system.action.return_to_launch()
        async for state in self.drone.system.telemetry.landed_state():
            if state == LandedState.ON_GROUND:
                logging.info("Drone landed successfully.")
                break
        logging.info("Drone landed. Exiting program...")
        return
