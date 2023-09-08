"""Implements the run_callable class attribute of the Land class."""

import asyncio

from ..land import Land
from ..start import Start
from ..state import State


async def run(self: Land) -> State:
    """Implements the run method."""
    print("Landing")
    await asyncio.sleep(1.0)
    return Start(self.drone)


Land.run_callable = run
