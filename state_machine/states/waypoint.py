"""Declares the Waypoint state class."""

from typing import Awaitable, Callable

from .state import State


class Waypoint(State):
    """The Waypoint state of the state machine."""

    run_callable: Callable[["Waypoint"], Awaitable[State]]

    @property
    def run(self) -> Callable[[], Awaitable[State]]:
        async def run() -> State:
            return await Waypoint.run_callable(self)

        return run
