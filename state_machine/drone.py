import asyncio
import mavsdk

class Drone:

    def __init__(self):
        self.system = mavsdk.System()

    async def connect_drone(self, connect: str = "udp://:14540"):
        await self.system.connect(system_address=connect)

    
    


    



