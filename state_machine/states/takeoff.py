from state_machine.states import State
from state_machine.states.waypoint import Waypoint

class Takeoff(State):
    """
    The Takeoff state of the state machine.
    """

    async def run(self) -> State:
        """
        Runs the Takeoff state of the state machine.
        """
        print("Taking Off")
        return Waypoint