from abc import ABC, abstractmethod
import logging
from typing import Awaitable

from ..drone import Drone


class State(ABC):
    """
    Defines the State abstract base class.

    This abstract base class serves as the foundation for all state types in the state machine.

    Attributes
    ----------
    _drone : Drone
        The drone to which this state is bound.

    Methods
    -------
    __init__(drone: Drone)
        Initialize a new state object.

    name() -> str
        Get the name of this state type.

    drone() -> Drone
        Get the drone this state is bound to.

    run() -> Awaitable["State"]
        Run this state.
    """

    def __init__(self, drone: Drone):
        """
        Initialize a new state object.

        Parameters
        ----------
        drone : Drone
            The drone to bind this state to.
        """
        self._drone: Drone = drone
        logging.info("Entering %s state", self.name)

    @property
    def name(self) -> str:
        """
        Get the name of this state type.

        Returns
        -------
        str
            The name of this state type.
        """
        return type(self).__name__

    @property
    def drone(self) -> Drone:
        """
        Get the drone this state is bound to.

        Returns
        -------
        Drone
            The drone object this state is bound to.
        """
        return self._drone

    @abstractmethod
    def run(self) -> Awaitable["State"]:
        """
        Run this state.

        This method must be implemented by subclasses to define the behavior of the state.

        Returns
        -------
        Awaitable["State"]
            An awaitable state representing the next state to transition to.
        """
