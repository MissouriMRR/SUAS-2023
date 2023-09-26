"""Defines the Drone class for the state machine."""

import mavsdk


class Drone:
    """A drone for the state machine to control."""

    def __init__(self, address: str = "udp://:14540") -> None:
        """Initialize a new Drone object."""
        self.system = mavsdk.System()
        self.address = address

    async def connect_drone(self) -> None:
        """Connect to a drone."""
        await self.system.connect(system_address=self.address)
