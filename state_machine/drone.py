"""Defines the Drone class for the state machine."""

import mavsdk


class Drone:
    """
    A drone for the state machine to control.
    This class is a wrapper around the mavsdk System class, and will be passed around to each state.
    Data can be stored in this class to be shared between states.
    """

    def __init__(self, address: str = "udp://:14540") -> None:
        """Initialize a new Drone object."""
        self.system = mavsdk.System()
        self.address = address

    async def connect_drone(self) -> None:
        """Connect to a drone."""
        await self.system.connect(system_address=self.address)
