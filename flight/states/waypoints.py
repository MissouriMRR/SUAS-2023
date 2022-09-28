"""Fly through the entire waypoint path after takeoff"""

import logging
from mavsdk import System
from flight.state_settings import StateSettings
from flight.states.state import State
from flight.states.odlcs import ODLC


class Waypoints(State):
    """
    State to run through waypoint flight path

    Attributes
    ----------
    None

    Methods
    -------
    run(drone: System) -> Union(Waypoints, ODLC)
        Process set of waypoints and fly within 25ft of each
    """
    async def run(self, drone: System) -> ODLC:
        """
        Run through list of waypoints & fly within 25ft of each desired point

        Parameters
        ----------
        drone : System
            MAVSDK object for manipulating drone position & attitude

        Returns
        -------
        Union[Waypoints, ODLC] : State
            Re-fly the waypoints if we failed to reach a waypoint boundary, or progress to ODLC flight stage
        """
        return ODLC(self.state_settings)
