"""Declares the Start state class."""

from typing import Awaitable, Callable, ClassVar

from .state import State


class Start(State):
    """The Start state of the state machine."""

    run_callable: ClassVar[Callable[["Start"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
