"""Implements the run_callable class attribute of the Waypoint class."""

# import asyncio
import time

# from ..land import Land
from ..state import State
from ..waypoint import Waypoint


async def run(self: Waypoint) -> State:
    """Implements the run method."""

    while True:
        time.sleep(0.5)
        print(f"{self} says: I am blocking everything else.")

    # try:
    #     print("Moving to waypoint")
    #     await asyncio.sleep(1.0)
    #     return Land(self.drone)
    # except asyncio.CancelledError as ex:
    #     print("Waypoint state canceled")
    #     raise ex
    # finally:
    #     pass


Waypoint.run_callable = run
