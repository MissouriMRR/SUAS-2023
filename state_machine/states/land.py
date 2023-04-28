from state_machine.states import State

class Land(State):
    """
    The Land state of the state machine.
    """

    async def run(self) -> State:
        """
        Runs the Land state of the state machine.
        """
        print("Landing")
        return None