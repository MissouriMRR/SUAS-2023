"""Implements the behavior of the Takeoff state."""
import asyncio
import logging

from json_functions import update_state

from state_machine.states.state import State
from state_machine.states.takeoff import Takeoff
from state_machine.states.waypoint import Waypoint


async def run(self: Takeoff) -> State:
    """
    Implements the run method for the Takeoff state.

    This method initiates the drone takeoff process and transitions to the Waypoint state.

    Returns
    -------
    Waypoint : State
        The next state after a successful takeoff.

    Raises
    ------
    asyncio.CancelledError
        If the execution of the Takeoff state is canceled.

    Notes
    -----
    This method is responsible for taking off the drone and transitioning it to the
    Waypoint state, which represents the navigation phase to reach a specified waypoint.

    """
    try:
        update_state("data.json", "Takeoff")
        logging.info("Takeoff state running")

        await self.drone.system.action.takeoff()

        return Waypoint(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Takeoff state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Takeoff class to the run function
Takeoff.run_callable = run
