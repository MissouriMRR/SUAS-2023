# Declares the Waypoint state class.
from typing import Awaitable, Callable, ClassVar

from .state import State

class Waypoint(State):
    """
    The Waypoint state of the state machine.

    This state represents the phase in which the drone is navigating to a specific waypoint.

    Attributes
    ----------
    run_callable : ClassVar[Callable[["Waypoint"], Awaitable[State]]]
        Class-level variable that holds a callable function signature.
        It's a Callable that takes an instance of Waypoint and returns an Awaitable[State].

    Methods
    -------
    run() -> Awaitable[State]:
        Execute the logic associated with the Waypoint state.

        This method is called to perform the logic associated with the Waypoint state.
        It should return an Awaitable[State], which represents the next state
        to transition to in the state machine.

        Returns
        -------
        Awaitable[State]
            The next state to transition to after reaching the specified waypoint.
    """
    
    run_callable: ClassVar[Callable[["Waypoint"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        """
        Execute the logic associated with the Waypoint state.

        Returns
        -------
        Awaitable[State]
            The next state to transition to after reaching the specified waypoint.
        """
        return self.run_callable()
