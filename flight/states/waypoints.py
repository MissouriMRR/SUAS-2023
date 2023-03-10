"""Fly through the entire waypoint path after takeoff"""

from mavsdk import System
from flight.states.state import State
from flight.states.odlcs import ODLC
from flight.Waypoint.goto import move_to
from flight import extract_gps
from flight.extract_gps import extract_gps, Waypoint, GPSData


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
        gps_dict: Waypoint = extract_gps("flight/data/waypoint_data.json")
        waypoints: GPSData = gps_dict["waypoints"]

        async for waypoint in waypoints:
            await move_to(drone, waypoint[0], waypoint[1], waypoint[2], 2 / 3)

        return ODLC(self.state_settings)
