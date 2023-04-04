"""Fly to each AirDrop location and release the payloads"""

from mavsdk import System
from flight.states.state import State
#from flight.states.odlcs import ODLC
from flight.states.land import Land


class AirDrop(State):
    """
    State to fly to each drop location and release the payloads to the corresponding standard object

    Methods
    -------
    run(drone: System) -> Land | ODLC
        Maneuver drone to each drop location and release the payloads onto corresponding standard ODLC
    """

    async def run(self, drone: System) -> Land:
        """
        Run through the located drop locations and release each payload

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position & attitude

        Returns
        -------
        Land | ODLC : State
            Progress to land the drone or re-scan the ODLC search area if an object was missed
        """
        return Land(self.state_settings)
