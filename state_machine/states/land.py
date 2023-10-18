# Declares the Land state class.
from typing import Awaitable, Callable, ClassVar

from .state import State

class Land(State):
    """
    The Land state of the state machine.

    Attributes:
        run_callable (ClassVar[Callable[["Land"], Awaitable[State]]]):
            Class-level variable to hold a callable function signature.
            It's a Callable that takes an instance of Land and returns an Awaitable[State].

    Methods:
        run() -> Awaitable[State]:
            Execute the logic associated with the Land state.

            This method is called to perform the logic associated with the Land state.
            It should return an Awaitable[State], which represents the next state
            to transition to in the state machine.

            Returns:
                Awaitable[State]: The next state to transition to.
    """

    run_callable: ClassVar[Callable[["Land"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        """
        Execute the logic associated with the Land state.

        This method is called to perform the logic associated with the Land state.
        It should return an Awaitable[State], which represents the next state
        to transition to in the state machine.

        Returns:
            Awaitable[State]: The next state to transition to.
        """
        return self.run_callable()
