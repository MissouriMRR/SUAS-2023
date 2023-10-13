"""Implements the run_callable class attribute of the Waypoint class."""

import asyncio
import logging

from ..land import Land
from ..state import State
from ..waypoint import Waypoint

from flight.waypoint.goto import move_to


async def run(self: Waypoint) -> State:
    """Implements the run method."""

    # try:
    print("Moving to waypoint")
    # await self.drone.system.action.goto_location(38, -92, 10, 0)
    await move_to(self.drone.system, 38, -92, 10, 0)
    return Land(self.drone)


Waypoint.run_callable = run
