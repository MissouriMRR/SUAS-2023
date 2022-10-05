"""Start state for the competition code"""

import logging
from mavsdk import System
from flight.state_settings import StateSettings
from flight.states.state import State
from flight.states.preprocess import PreProcess


class Start(State):
    """
    Preliminary state to initiate state machine

    Attributes
    ----------
    None

    Methods
    -------
    begin(drone: System) -> PreProcess
        Start the state machine & proceed to PreProcess state
    """

    async def begin(self, drone: System) -> PreProcess:
        """
        Start state machine and pass to PreProcess state

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        PreProcess : State
            Next state to generate flight paths
        """
        logging.debug("Start state machine")
        return PreProcess(self.state_settings)
