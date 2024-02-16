"""Tests the state machine."""

import asyncio
import logging
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
import time
from mavsdk.telemetry import FlightMode, LandedState

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import Start
from state_machine.states.state import State
from state_machine.flight_settings import FlightSettings


class FlightManager:
    """
    Class that manages the state machine, kill switch, and gracefully exiting the program.

    Methods
    -------
    __init__(self) -> None
        Initialize a flight manager object.
    start_manager() -> None
        Test running the state machine in a separate process.
        Sets the drone address to the simulation or physical address.
    start_state_machine(drone: Drone) -> None
        Create and start a state machine in the event loop. This method should
        be called in its own process.
    start_kill_switch(state_machine_process: Process, drone: Drone) -> None
        Create and start a kill switch in the event loop.
    kill_switch(state_machine_process: Process, drone: Drone) -> Awaitable[None]
        Enable the kill switch and wait until it activates. The drone should be
        in manual mode after this method returns.
    graceful_exit(drone: Drone) -> Awaitable[None]
        Lands the drone and exits the program.
    """

    def __init__(self) -> None:
        self.drone: Drone = Drone()

    def start_manager(self, sim_flag: bool) -> None:
        """
        Test running the state machine in a separate process.
        Sets the drone address to the simulation or physical address.

        Parameters
        ----------
        sim_flag: bool
            A flag representing if the the drone is a simulation.
        """
        if sim_flag is True:
            self.drone.address = "udp://:14540"
        else:
            self.drone.address = "serial:///dev/ttyUSB0:921600"
        flight_settings_obj: FlightSettings = FlightSettings()

        # Initialize a pipe for communication between the processes
        state_parent_pipe: Connection  # We shall send this to the state machine
        state_child_pipe: Connection  # We shall send this to the kill switch to receive states
        state_parent_pipe, state_child_pipe = Pipe(False)

        logging.info("Starting processes")
        state_machine: Process = Process(
            target=self.start_state_machine,
            args=(
                flight_settings_obj,
                state_parent_pipe,
            ),
        )
        kill_switch_process: Process = Process(
            target=self.start_kill_switch,
            args=(
                state_machine,
                state_child_pipe,
            ),
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
            asyncio.run(self.graceful_exit())

    def start_state_machine(
        self, flight_settings: FlightSettings, pipe: Connection, initial_state: State | None = None
    ) -> None:
        """
        Create and start a state machine in the event loop. This method should
        be called in its own process.

        Parameters
        ----------
        flight_settings: FlightSettings
            The flight settings to use.
        """
        if initial_state is None:
            initial_state = Start(self.drone, flight_settings)
        logging.info("-- Starting state machine")
        asyncio.run(StateMachine(initial_state, self.drone, flight_settings, pipe).run())

    def start_kill_switch(self, process: Process, pipe: Connection) -> None:
        """
        Create and run a kill switch in the event loop.

        Parameters
        ----------
        state_machine_process : Process
            The process running the state machine to kill.
        """
        logging.info("-- Starting kill switch")
        asyncio.run(self.kill_switch(process, pipe))

    async def kill_switch(self, state_machine_process: Process, pipe: Connection) -> None:
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

        async for flight_mode in self.drone.system.telemetry.flight_mode():
            while flight_mode != FlightMode.POSCTL:
                time.sleep(1)

        logging.critical("Kill switch activated. Terminating state machine.")
        state_machine_process.terminate()

        # Get latest state sent through the pipe
        state: State = Start(self.drone, FlightSettings())
        while True:
            if pipe.poll() is False:
                break
            state = pipe.recv()
            print(state)
            print(type(state))
            return

        # Gotta wait for user input here
        logging.critical("Press enter to restart the state machine.")
        input()
        state_machine: Process = Process(
            target=self.start_state_machine,
            args=(
                FlightSettings(),
                pipe,
                state,
            ),
        )
        state_machine.start()
        await self.kill_switch(state_machine, pipe)

    async def graceful_exit(self) -> None:
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
