"""Implements the run_callable class attribute of the Waypoint class."""

import asyncio

from ..land import Land
from ..state import State
from ..waypoint import Waypoint


async def run(self: Waypoint) -> State:
    """Implements the run method."""
    try:
        print("Moving to waypoint")
        await asyncio.sleep(1.0)
        return Land(self.drone)
    except asyncio.CancelledError as ex:
        print("Waypoint state canceled")
        raise ex
    finally:
        pass


Waypoint.run_callable = run
