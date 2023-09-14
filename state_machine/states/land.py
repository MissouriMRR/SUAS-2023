"""Declares the Land state class."""

from typing import Awaitable, Callable, ClassVar

from .state import State


class Land(State):
    """The Land state of the state machine."""

    run_callable: ClassVar[Callable[["Land"], Awaitable[State]]]

    def run(self) -> Awaitable[State]:
        return self.run_callable()
