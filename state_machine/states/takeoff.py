# Declares the Takeoff state class.
from typing import Awaitable, Callable, ClassVar

from .state import State

class Takeoff(State):
    """
    The Takeoff state of the state machine.

    This state represents the phase in which the drone is taking off.

    Attributes
    ----------
    run_callable : ClassVar[Callable[["Takeoff"], Awaitable[State]]]
        Class-level variable that holds a callable function signature.
        It's a Callable that takes an instance of Takeoff and returns an Awaitable[State].

    Methods
    -------
    run() -> Awaitable[State]:
        Execute the logic associated with the Takeoff state.

        This method is called to perform the logic associated with the Takeoff state.
        It should return an Awaitable[State], which represents the next state
        to transition to in the state machine.

        Returns
        -------
        Awaitable[State]
            The next state to transition to after the Takeoff phase is complete.
    """
    
    run_callable: ClassVar[Callable[["Takeoff"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        """
        Execute the logic associated with the Takeoff state.

        Returns
        -------
        Awaitable[State]
            The next state to transition to after the Takeoff phase is complete.
        """
        return self.run_callable()
