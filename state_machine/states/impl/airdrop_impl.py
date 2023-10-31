"""Implements the behavior of the Airdrop state."""
import asyncio
import logging

from state_machine.states.airdrop import Airdrop
from state_machine.states.waypoint import Waypoint
from state_machine.states.state import State


async def run(self: Airdrop) -> State:
    """
    Implements the run method for the Airdrop state.

    This method initiates the Airdrop process of the drone and transitions to the Waypoint state.

    Returns
    -------
    Waypoint : State
        The next state after the drone has successfully completed the Airdrop.

    Notes
    -----
    This method is responsible for initiating the Airdrop process of the drone and transitioning
    it back to the Waypoint state.

    """
    try:
        logging.info("Airdrop")

        # code for Airdrop logic

        return Waypoint(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Airdrop state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Airdrop class to the run function
Airdrop.run_callable = run
