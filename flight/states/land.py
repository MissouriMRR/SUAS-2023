"""Safely land the drone after all other tasks have been completed"""

from mavsdk import System
from flight.states.state import State
from flight.states.final import Final


class Land(State):
    """
    State to safely land the drone after other SUAS objectives have been finished

    Methods
    -------
    run(drone: System) -> Final
        Land the drone safely from operational altitude
    """

    async def run(self, drone: System) -> Final:
        """
        Maneuver the drone to the landing location and safely land the drone

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        Final : State
            Last state to end state machine
        """
        return Final(self.state_settings)
