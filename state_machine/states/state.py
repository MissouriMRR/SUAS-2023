"""Defines the State abstract base class, which all states should inherit from."""

from abc import ABC, abstractmethod
import logging
from typing import Awaitable

from state_machine.drone import Drone
from state_machine.flight_settings import FlightSettings


class State(ABC):
    """
    Defines the State abstract base class, which all states should inherit from.

    This abstract base class serves as the foundation for all state types in the state machine.

    Attributes
    ----------
    _drone : Drone
        The drone to which this state is bound.
    _flight_settings : FlightSettings
        The flight settings to which this state is bound.

    Methods
    -------
    __init__(drone: Drone, flight_settings: FlightSettings) -> None
        Initialize a new state object.

    name() -> str
        Get the name of this state type.

    drone() -> Drone
        Get the drone this state is bound to.

    flight_settings() -> FlightSettings
        Get the flight settings this state is bound to.

    run() -> Awaitable["State"]
        Run this state.
    """

    def __init__(self, drone: Drone, flight_settings: FlightSettings) -> None:
        """
        Initialize a new state object.

        Parameters
        ----------
        drone : Drone
            The drone to bind this state to.
        flight_settings : FlightSettings
            The drone to bind this state to.
        """
        self._drone: Drone = drone
        self._flight_settings: FlightSettings = flight_settings
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

    @property
    def flight_settings(self) -> FlightSettings:
        """
        Get the flight settings this state is bound to.

        Returns
        -------
        Drone
            The flight settings object this state is bound to.
        """
        return self._flight_settings

    @abstractmethod
    def run(self) -> Awaitable["State"] | Awaitable[None]:
        """
        Execute the logic associated with this state and return the next state
        to transition to.

        This method must be implemented by subclasses to define the behavior of the state.

        Returns
        -------
        Awaitable["State"]
            An awaitable state representing the next state to transition to.
        """
        # type: ignore
