import asyncio
import mavsdk

class Drone:

    def __init__(self):
        self.drone = mavsdk.System()

    async def connect_drone(self, connect: str = "udp://:14540"):
        await self.drone.connect(system_address=connect)



