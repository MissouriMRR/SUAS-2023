import asyncio
import logging

from ..land import Land
from ..state import State
from ..waypoint import Waypoint

from flight.waypoint.goto import move_to


async def run(self: Waypoint) -> State:
    """
    Run method implementation for the Waypoint state.

    This method instructs the drone to navigate to a specified waypoint and transitions to the Land state upon arrival.

    Parameters
    ----------
    self : Waypoint
        An instance of the Waypoint state.

    Returns
    -------
    Land : State
        The next state after successfully reaching the specified waypoint and initiating the landing process.

    Raises
    ------
    asyncio.CancelledError
        If the execution of the Waypoint state is canceled.

    Notes
    -----
    This method is responsible for guiding the drone to a predefined waypoint in its flight path.
    Upon reaching the waypoint, it transitions the drone to the Land state to initiate landing.

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


# Set the run_callable attribute of the Waypoint class to the run function
Waypoint.run_callable = run
