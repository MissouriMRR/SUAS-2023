"""Implements the run_callable class attribute of the Land class."""

import asyncio
import logging

from ..land import Land
from ..start import Start
from ..state import State


async def run(self: Land) -> State:
    """Implements the run method."""
    try:
        logging.info("Landing")
        await self.drone.system.action.land()
        return Start(self.drone)
    except asyncio.CancelledError as ex:
        print("Land state canceled")
        raise ex
    finally:
        pass


Land.run_callable = run
