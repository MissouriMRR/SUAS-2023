"""Implements the behavior of the Land state."""
import asyncio
import logging

from json_functions import update_state

from state_machine.states.land import Land
from state_machine.states.start import Start
from state_machine.states.state import State


async def run(self: Land) -> State:
    """
    Implements the run method for the Land state.

    This method initiates the landing process of the drone and transitions to the Start state.

    Returns
    -------
    Start : State
        The next state after the drone has successfully landed.

    Notes
    -----
    This method is responsible for initiating the landing process of the drone and transitioning
    it back to the Start state, preparing for a new flight.

    """
    try:
        update_state("data.json", "Land")
        logging.info("Landing")

        # Instruct the drone to land
        await self.drone.system.action.land()

        return Start(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Land state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Land class to the run function
Land.run_callable = run
