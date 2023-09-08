"""Implements the run_callable class attribute of the Takeoff class."""

import asyncio

from ..state import State
from ..takeoff import Takeoff
from ..waypoint import Waypoint


async def run(self: Takeoff) -> State:
    """Implements the run method."""
    print("Taking off")
    await asyncio.sleep(1.0)
    return Waypoint(self.drone)


Takeoff.run_callable = run
