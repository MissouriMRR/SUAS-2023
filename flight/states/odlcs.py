"""Fly througn ODLC search area and search for all 5 objects"""

from mavsdk import System
from flight.states.state import State
from flight.states.airdrop import AirDrop


class ODLC(State):
    """
    State to fly through ODLC search grid and scan for standard & emergent objects

    Methods
    -------
    run(drone: System) -> AirDrop
        Run ODLC flight algorithm and pass to next state
    """

    async def run(self, drone: System) -> AirDrop:
        """
        Fly through the ODLC search area and look for the 5 standard objects and emergent object

        Parameters
        ----------
        drone : System
            MAVSDK drone object to manipulate drone position & attitude

        Returns
        -------
        AirDrop : State
            The next state in the state machine, AirDrop for the payloads
        """
        return AirDrop(self.state_settings)
