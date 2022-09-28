"""Fly to each AirDrop location and release the payloads"""

import logging
from mavsdk import System
from typing import Union
from flight.state_settings import StateSettings
from flight.states.state import State
from flight.states.odlcs import ODLC
from flight.states.land import Land


class AirDrop(State):
    """
    State to fly to each drop location and release the paylods to the corresponding standard object

    Attributes
    ----------
    None

    Methods
    -------
    run(drone: System) -> Union[Land, ODLC]
        Maneuver drone to each drop location and release the payloads onto corresponding standard ODLC
    """
    async def run(self, drone: System) -> Union[Land, ODLC]:
        """
        Run through the located drop locations and release each payload

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position & attitude

        Returns
        -------
        Union(Land, ODLC) : State
            Progress to land the drone or re-scan the ODLC search area if an object was missed
        """
        return Land(self.state_settings)
