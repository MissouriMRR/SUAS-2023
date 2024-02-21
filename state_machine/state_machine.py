"""Defines the StateMachine class."""

import asyncio
from asyncio import Task
import logging

from state_machine.drone import Drone
from state_machine.flight_settings import FlightSettings
from state_machine.states import State


class StateMachine:
    """
    A state machine controlling a drone.

    Attributes
    ----------
    current_state : State
        The state this state machine is currently running.
    drone : Drone
        The drone this state machine controls.
    flight_settings : FlightSettings
        The flight settings this flight uses.
    run_task : Task[None] | None
        The task that runs through the states in a loop. If the state machine
        is not running, this should be None.

    Methods
    -------
    __init__(initial_state: State, drone: Drone, flight_settings: FlightSettings)
        Initialize a new state machine object.
    run(initial_state: State | None) -> Awaitable[None]
        Run the flight code specific to each state until completion.
    cancel() -> Awaitable[None]
        Cancel the currently running state loop.
    """

    def __init__(self, initial_state: State, drone: Drone, flight_settings: FlightSettings):
        """
        Initialize a new state machine object.

        Parameters
        ----------
        initial_state : State
            The first state that runs when the state machine is started by the
            `run()` method.
        drone : Drone
            The drone this state machine will control.
        flight_settings : FlightSettings
            The flight settings to use.
        """
        self.current_state: State | None = initial_state
        self.drone: Drone = drone
        self.flight_settings: FlightSettings = flight_settings
        self.run_task: Task[None] | None = None

    async def run(self, initial_state: State | None = None) -> None:
        """Run the flight code specific to each state until completion.

        Parameters
        ----------
        initial_state : State | None
            If provided, sets the state machine's current state. This must
            share the same drone and flight settings as this state machine.
        """
        if self.run_task is not None:
            return

        if initial_state is not None:
            self.current_state = initial_state

        run_task: Task[None] = asyncio.ensure_future(self._run())
        self.run_task = run_task
        logging.info("State Machine started")
        await run_task
        if self.run_task is not None:
            self.run_task = None
            logging.info("State Machine complete")

    async def _run(self) -> None:
        """Runs the flight code specific to each state until completion."""
        while self.current_state:
            self.current_state = await self.current_state.run()

    def cancel(self) -> None:
        """Cancel the currently running state loop.."""
        if self.run_task is None:
            return

        self.run_task.cancel()
        self.run_task = None
        logging.info("State Machine canceled")
