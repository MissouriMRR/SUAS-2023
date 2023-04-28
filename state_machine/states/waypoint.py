from state_machine.states import State
from state_machine.states.land import Land

class Waypoint(State):
    """
    The Waypoint state of the state machine.
    """

    async def run(self) -> State:
        """
        Runs the Waypoint state of the state machine.
        """
        print("Flying to Waypoint")
        return Land