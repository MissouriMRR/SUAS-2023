import asyncio
import logging

from ..land import Land
from ..state import State
from ..waypoint import Waypoint

from flight.waypoint.goto import move_to


async def run(self: Waypoint) -> State:
    """
    Implements the run method for the Waypoint state.

    This method instructs the drone to move to a specified waypoint and transitions to the Land state.

    Parameters
    ----------
    self : Waypoint
        An instance of the Waypoint state.

    Returns
    -------
    Land : State
        The next state after reaching the specified waypoint and landing.

    Raises
    ------
    asyncio.CancelledError
        If the execution of the Waypoint state is canceled.

    Notes
    -----
    This method is responsible for instructing the drone to navigate to a specified waypoint.
    Once the waypoint is reached, the drone transitions to the Land state.

    """
    try:
        logging.info("Waypoint state running")
        print("Moving to waypoint")
        
        # Use the move_to function to navigate to the waypoint
        await move_to(self.drone.system, 38, -92, 10, 0)
        
        return Land(self.drone)
    except asyncio.CancelledError as ex:
        logging.error("Waypoint state canceled")
        raise ex
    finally:
        pass

# Setting the run_callable attribute of the Waypoint class to the run function
Waypoint.run_callable = run
