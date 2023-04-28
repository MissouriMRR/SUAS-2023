from state_machine.states import State
from state_machine.states.takeoff import Takeoff
import logging

class Start(State):
    """
    The Start state of the state machine.
    """

    async def run(self) -> State:
        """
        Runs the Start state of the state machine.
        """
        print("Starting State Machine")
        print("Waiting for drone to connect...")
        await self.connect_drone()
        print("Starting State Machine")
        return Takeoff