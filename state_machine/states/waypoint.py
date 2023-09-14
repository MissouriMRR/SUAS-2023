"""Declares the Waypoint state class."""

from typing import Awaitable, Callable, ClassVar

from .state import State


class Waypoint(State):
    """The Waypoint state of the state machine."""

    run_callable: ClassVar[Callable[["Waypoint"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
