"""Fly through the entire waypoint path after takeoff"""

from mavsdk import System
from flight.states.state import State
from flight.states.odlcs import ODLC


class Waypoints(State):
    """
    State to run through waypoint flight path

    Methods
    -------
    run(drone: System) -> ODLC
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
        ODLC : State
            Re-fly the waypoints if we failed to reach a waypoint boundary, or progress to ODLC flight stage
        """
        return ODLC(self.state_settings)
