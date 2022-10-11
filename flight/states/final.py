"""Empty state to signal the end of the state machine"""

import logging
from mavsdk import System
from flight.states.state import State


class Final(State):
    """
    Last state in the state machine to end the competition code

    Methods
    -------
    run(drone: System) -> None
        Does nothing and ends state machine
    """

    async def run(self, drone: System) -> None:
        """
        Do nothing state to log end of competition code and terminate state machine

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude
        """
        logging.debug("End of state machine.")
        return None
