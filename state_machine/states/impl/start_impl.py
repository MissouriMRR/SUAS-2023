"""Implements the run method of the Start state class."""

import asyncio

from ..start import Start
from ..state import State
from ..takeoff import Takeoff


async def run(self: Start) -> State:
    """Implements the run method."""
    print("Starting")
    await asyncio.sleep(1.0)
    return Takeoff(self.drone)


Start.run_callable = run
