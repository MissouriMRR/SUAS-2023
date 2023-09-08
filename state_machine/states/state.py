"""Defines the State abstract base class."""

from abc import ABC, abstractmethod
import logging
from typing import Awaitable, Callable

from ..drone import Drone


class State(ABC):
    """The abstract base class of state types."""

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
        """Get the name of this state type."""
        return type(self).__name__

    @property
    def drone(self) -> Drone:
        """Get the drone this state is bound to."""
        return self._drone

    @property
    @abstractmethod
    def run(self) -> Callable[[], Awaitable["State"]]:
        """Get an async callable bound to this object that runs this state."""
