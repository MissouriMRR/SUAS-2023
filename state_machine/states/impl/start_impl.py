"""Implements the run_callable class attribute of the Start class."""

import asyncio

from ..start import Start
from ..state import State
from ..takeoff import Takeoff


async def run(self: Start) -> State:
    """Implements the run method."""
    try:
        print("Starting")
        await asyncio.sleep(1.0)
        return Takeoff(self.drone)
    except asyncio.CancelledError as ex:
        print("Start state canceled")
        raise ex
    finally:
        pass


Start.run_callable = run
