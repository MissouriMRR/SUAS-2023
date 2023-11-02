"""Implements the behavior of the ODLC state."""
import asyncio
import logging

from state_machine.states.airdrop import Airdrop
from state_machine.states.odlc import ODLC
from state_machine.states.state import State


async def run(self: ODLC) -> State:
    """
    Implements the run method for the ODLC state.

    Returns
    -------
    Airdrop : State
        The next state after the drone has successfully scanned the ODLC area.

    Notes
    -----
    This method is responsible for initiating the ODLC scanning process of the drone
    and transitioning it to the Airdrop state.
    """
    try:
        logging.info("ODLC")
        # code for the ODLC logic

        return Airdrop(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("ODLC state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the ODLC class to the run function
ODLC.run_callable = run
