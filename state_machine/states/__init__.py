from mavsdk import System
from state_machine.drone import Drone
import logging

class State:

    def __init__(self, drone: Drone) -> None:
        self.drone = drone
        logging.info(f"Starting state: {self.name}")

    async def run(self):
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

    @property
    def name(self) -> str:
        return type(self).__name__