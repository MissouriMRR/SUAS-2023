"""Implements the run method of the Waypoint state class."""

import asyncio

from ..land import Land
from ..state import State
from ..waypoint import Waypoint


async def run(self: Waypoint) -> State:
    """Implements the run method."""
    print("Moving to waypoint")
    await asyncio.sleep(1.0)
    return Land(self.drone)


Waypoint.run_callable = run
