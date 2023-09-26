"""Implements the run_callable class attribute of the Takeoff class."""

import asyncio
import logging

from ..state import State
from ..takeoff import Takeoff
from ..waypoint import Waypoint


async def run(self: Takeoff) -> State:
    """Implements the run method."""
    try:
        logging.info("Takeoff state running")
        
        await self.drone.system.action.takeoff()
        
        
        
        return Waypoint(self.drone)
    except asyncio.CancelledError as ex:
        print("Takeoff state canceled")
        raise ex
    finally:
        pass


Takeoff.run_callable = run
