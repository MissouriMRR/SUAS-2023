"""Run takeoff function to raise the drone to our desired altitude"""

import asyncio
import config
import logging
from mavsdk import System
from flight.states.state import State
from flight.states.waypoints import Waypoints


class Takeoff(State):
    """
    Runs takeoff procedure to lift the drone to preset altitude

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
        # Initialize altitude (convert feet to meters)
        await drone.action.set_takeoff_altitude(config.TAKEOFF_ALT / 3.2808)

        # Arm drone and takeoff
        logging.info("Arming Drone")
        await drone.action.arm()

        logging.info("Taking off")
        await drone.action.takeoff()

        # Wait for drone to take off
        await asyncio.sleep(2)

        # Go to Waypoint State
        return Waypoints(self.state_settings)
