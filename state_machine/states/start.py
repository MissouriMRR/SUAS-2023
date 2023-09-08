"""Declares the Start state class."""

from typing import Awaitable, Callable

from .state import State


class Start(State):
    """The Start state of the state machine."""

    run_callable: Callable[["Start"], Awaitable[State]]

    @property
    def run(self) -> Callable[[], Awaitable[State]]:
        def run() -> Awaitable[State]:
            return Start.run_callable(self)

        return run
