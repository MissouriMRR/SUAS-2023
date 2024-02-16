"""Declares the Takeoff state class."""

from typing import Awaitable, Callable, ClassVar

from state_machine.states.state import State


class Takeoff(State):
    """
    The Takeoff state of the state machine.

    This state represents the phase in which the drone is taking off.

    Attributes
    ----------
    run_callable : ClassVar[Callable[["Takeoff"], Awaitable[State]]]
        The callable object to call when this state is run. This object is
        shared between all instances of this class.

    Methods
    -------
    run() -> Awaitable[State]:
        Execute the logic associated with this state and return the next state
        to transition to.
    """

    run_callable: ClassVar[Callable[["Takeoff"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
