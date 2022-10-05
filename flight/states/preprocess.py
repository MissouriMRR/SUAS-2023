"""Generate a flight path for the waypoints within the flight boundaries"""

import logging
from mavsdk import System
from flight.state_settings import StateSettings
from flight.states.state import State
from flight.states.takeoff import Takeoff


class PreProcess(State):
    """
    State to generate flight paths for competition

    Attributes
    ----------
    None

    Methods
    -------
    run(drone: System) -> Takeoff
        Generate an in-bounds flight path from the given GPS data
    """

    async def run(self, drone: System) -> Takeoff:
        """
        Given GPS coordinates of boundary & waypoints, create efficient flight path

        Parameters
        ----------
        drone : System

        Returns
        -------
        Takeoff : State
            Next state to lift drone off the ground
        """
        return Takeoff(self.state_settings)
