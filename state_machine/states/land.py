"""Declares the Land state class."""

from typing import Awaitable, Callable, ClassVar

from state_machine.states.state import State


class Land(State):
    """
    The Land state of the state machine.

    Attributes
    ----------
    run_callable : ClassVar[Callable[["Land"], Awaitable[State]]]
        The callable object to call when this state is run. This object is
        shared between all instances of this class.

    Methods
    -------
    run() -> Awaitable[State]:
        Execute the logic associated with this state and return the next state
        to transition to.
    """

    run_callable: ClassVar[Callable[["Land"], Awaitable[None]]]

    def run(self) -> Awaitable[None]:
        return self.run_callable()
