"""Declares the Land state class."""

from typing import Awaitable, Callable

from .state import State


class Land(State):
    """The Land state of the state machine."""

    run_callable: Callable[["Land"], Awaitable[State]]

    @property
    def run(self) -> Callable[[], Awaitable[State]]:
        def run() -> Awaitable[State]:
            return Land.run_callable(self)

        return run
