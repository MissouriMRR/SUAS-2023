"""Defines the StateMachine class."""

import logging

from .drone import Drone
from .states import State


class StateMachine:
    """A state machine controlling a drone."""

    def __init__(self, initial_state: State, drone: Drone) -> None:
        self.current_state: State = initial_state
        self.drone: Drone = drone

    async def run(self) -> None:
        """
        Runs the flight code specific to each state until completion
        """
        while self.current_state:
            self.current_state = await self.current_state.run()

        logging.info("State Machine Complete")
        return
