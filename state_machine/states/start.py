"""Declares the Start state class."""

from typing import Awaitable, Callable, ClassVar

from state_machine.states.state import State


class Start(State):
    """
    The Start state of the state machine.

    Attributes
    ----------
    run_callable : Callable[["Start"], Awaitable[State]]
        The callable object to call when this state is run. This object is
        shared between all instances of this class.

    Methods
    -------
    run() -> Awaitable[State]:
        Execute the logic associated with this state and return the next state
        to transition to.
    """

    run_callable: ClassVar[Callable[["Start"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
