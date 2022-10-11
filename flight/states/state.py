"""Base state class for competition stages"""

import logging
from mavsdk import System
from flight.state_settings import StateSettings


class State:
    """
    Base flight state class

    Attributes
    ----------
    state_settings : StateSettings
        Parameters of flight plan, i.e. title description, etc.

    Methods
    -------
    run(drone: System)
        Runs the code for each state and return the next, or None if at the end of the state machine
        For the base class, NotImplementedError is raised
    check_arm_or_arm(drone: System) -> None
        Verifies if drone is armed, and if not, arms it
    """

    def __init__(self, state_settings: StateSettings) -> None:
        """
        Initializes base state with mission's Settings

        Parameters
        ----------
        state_settings : StateSettings
            Flight mission attributes & competition data
        """
        logging.info("State %s has begun", self.name)
        self.state_settings: StateSettings = state_settings

    async def run(self, drone: System):
        """
        Flight mission code for each state

        Parameters
        ----------
        drone : System
            MAVSDK drone object used to manipulate drone position & attitude

        Raises
        ------
        NotImplementedError
            Since this is the base State class, this run() function should not be utilized.
        """
        raise NotImplementedError("Base class function should not be called.")

    async def check_arm_or_arm(self, drone: System) -> None:
        """
        Determines if drone has armed, and if not, proceeds to arm it

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position & attitude
        """
        async for is_armed in drone.telemetry.armed():
            if not is_armed:
                logging.debug("Drone not armed. Attempting to arm...")
                await drone.action.arm()
            else:
                logging.warning("Drone armed.")
                break

    @property
    def name(self):
        """
        Getter function to return name & type of state

        Returns
        -------
        name : State
            Name of current state
        """
        return type(self).__name__

