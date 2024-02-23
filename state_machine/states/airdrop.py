"""Declares the Airdrop state class."""

from typing import Awaitable, Callable, ClassVar

from state_machine.states.state import State


class Airdrop(State):
    """
    The Airdrop state of the state machine.

    This state represents the phase in which the drone will drop waterbottles on targets.

    Attributes
    ----------
    run_callable : ClassVar[Callable[["Waypoint"], Awaitable[State]]]
        The callable object to call when this state is run. This object is
        shared between all instances of this class.

    Methods
    -------
    run(self) -> Awaitable[State]:
        Execute the logic associated with this state and return the next state
        to transition to.
    """

    run_callable: ClassVar[Callable[["Airdrop"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
