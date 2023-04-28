import logging

from state_machine.states import State
from state_machine.drone import Drone

class StateMachine:

    def __init__(self, initial_state: State, drone: Drone) -> None:
        self.current_state: State = initial_state
        self.drone: Drone = drone

    async def run(self) -> None:
        """
        Runs the flight code specific to each state until completion
        """
        while self.current_state:
            if self.current_state == None:
                break
            self.current_state = await self.current_state.run(self.drone)
        logging.info("State Machine Complete")
        return

