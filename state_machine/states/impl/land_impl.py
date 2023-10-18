import asyncio
import logging

from ..land import Land
from ..start import Start
from ..state import State


async def run(self: Land) -> State:
    """
    Implements the run method for the Land state.

    This method initiates the landing process of the drone and transitions to the Start state.

    Parameters
    ----------
    self : Land
        An instance of the Land state.

    Returns
    -------
    Start : State
        The next state after the drone has successfully landed.

    Raises
    ------
    asyncio.CancelledError
        If the execution of the Land state is canceled.

    Notes
    -----
    This method is responsible for initiating the landing process of the drone and transitioning
    it back to the Start state, preparing for a new flight.

    """
    try:
        logging.info("Landing")

        # Instruct the drone to land
        await self.drone.system.action.land()

        return Start(self.drone)
    except asyncio.CancelledError as ex:
        logging.error("Land state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Land class to the run function
Land.run_callable = run
