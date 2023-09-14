"""Declares the Takeoff state class."""

from typing import Awaitable, Callable, ClassVar

from .state import State


class Takeoff(State):
    """The Takeoff state of the state machine."""

    run_callable: ClassVar[Callable[["Takeoff"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
