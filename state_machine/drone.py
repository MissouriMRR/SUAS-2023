"""Defines the Drone class for the state machine."""

import mavsdk


class Drone:
    """
    A drone for the state machine to control.
    This class is a wrapper around the mavsdk System class, and will be passed around to each state.
    Data can be stored in this class to be shared between states.

    Attributes
    ----------
    system : mavsdk.System
        The MAVSDK system object that controls the drone.
    address : str
        The address used to connect to the drone when the `connect_drone()`
        method is called.
    odlc_scan : bool
        A boolean to tell if the odlc zone needs to be scanned, used the
        first run and if odlc needs to be scanned any other time
    Methods
    -------
    __init__(address: str) -> None
        Initialize a new Drone object, but do not connect to a drone.
    connect_drone(self) -> Awaitable[None]
        Connect to a drone.
    """

    def __init__(self, address: str = "udp://:14540") -> None:
        """
        Initialize a new Drone object, but do not connect to a drone.

        Parameters
        ----------
        address : str
            The address of the drone to connect to when the `connect_drone()`
            method is called.
        """
        self.system: mavsdk.System = mavsdk.System()
        self.address: str = address
        self.odlc_scan: bool = True

    async def connect_drone(self) -> None:
        """Connect to a drone."""
        await self.system.connect(system_address=self.address)
