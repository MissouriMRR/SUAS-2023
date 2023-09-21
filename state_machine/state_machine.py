"""Defines the StateMachine class."""

import asyncio
from asyncio import Task
import logging

from .drone import Drone
from .states import State


class StateMachine:
    """A state machine controlling a drone."""

    def __init__(self, initial_state: State, drone: Drone) -> None:
        self.current_state: State = initial_state
        self.drone: Drone = drone
        self.run_task: Task[None] | None = None

    async def run(self, initial_state: State | None = None) -> None:
        """Runs the flight code specific to each state until completion.

        Parameters
        ----------
        initial_state : State | None
            If provided, sets the state machine's current state.
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
        """Cancel the state machine's state loop."""
        if self.run_task is None:
            return

        self.run_task.cancel()
        self.run_task = None
        logging.info("State Machine canceled")
