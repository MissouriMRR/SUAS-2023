"""Declares the Takeoff state class."""

from typing import Awaitable, Callable

from .state import State


class Takeoff(State):
    """The Takeoff state of the state machine."""

    run_callable: Callable[["Takeoff"], Awaitable[State]]

    @property
    def run(self) -> Callable[[], Awaitable[State]]:
        async def run() -> State:
            return await Takeoff.run_callable(self)

        return run
