"""Run takeoff function to raise the drone to our desired altitude"""

import logging
from mavsdk import System
from flight.state_settings import StateSettings
from flight.states.state import State
from flight.states.waypoints import Waypoints


class Takeoff(State):
    """
    Runs takeoff procedure to lift the drone to preset altitude

    Attributes
    ----------
    None

    Methods
    -------
    run(drone: System) -> Waypoints
        Lift the drone from takeoff location and begin movement to first waypoint
    """
    async def run(self, drone: System) -> Waypoints:
        """
        Run takeoff procedure to move drone upwards using offboard or action functions

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        Waypoints : State
            Next state to fly waypoint path
        """
        return Waypoints(self.state_settings)

