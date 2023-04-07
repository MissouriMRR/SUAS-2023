"""Fly to each AirDrop location and release the payloads"""

import asyncio
from math import sqrt
from mavsdk import System
from flight.maestro.air_drop import Airdrop_Control
from flight.states.state import State
from flight.states.odlcs import ODLC
from flight.states.land import Land
from flight.goto import move_to

class AirDrop(State):
    """
    State to fly to each drop location and release the payloads to the corresponding standard object

    Methods
    -------
    run(drone: System) -> Land | ODLC
        Maneuver drone to each drop location and release the payloads onto corresponding standard ODLC
    """

    async def run(self, drone: System) -> Land | ODLC:
        """
        Run through the located drop locations and release each payload

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position & attitude

        Returns
        -------
        Land | ODLC : State
            Progress to land the drone or re-scan the ODLC search area if an object was missed
        """

        airdrop = Airdrop_Control()

        # Vision guys will give a dict using this format for the bottle locations:
        # bottle_dict : {
        #   0: ["latitude": 1, "longitude": 2],
        #   1: ...,
        # }
        # We will use a sample one for now!
        bottle_locations = {
            1: {"latitude": 37.901096681, "longitude": -91.6658804},
            2: {"latitude": 37.9009907274, "longitude": -91.66255949},
            3: {"latitude": 37.89915707, "longitude": -91.663931618},
            4: {"latitude": 37.89783936, "longitude": -91.661258865},
            5: {"latitude": 37.900769059, "longitude": -91.665224920},
        }

        for range in range(len(bottle_locations)):
            print('Bottle drop #', range, 'started')
            lowest_distance: float
            lowest_distance_bottle: int
            async for position in drone.telemetry.position():
                current_location = position
                break
            for location in bottle_locations.values():
                distance = await self.get_distance(
                    current_location.latitude_deg,
                    current_location.longitude_deg,
                    location["latitude"],
                    location["longitude"],
                )
                if distance < lowest_distance:
                    lowest_distance = distance
                    bottle_loc = location
                    bottle_num = {i for i in bottle_locations if bottle_locations[i]==location}
            print('Nearest bottle: #', range, 'at', bottle_loc["latitude"], bottle_loc["longitude"])
            await move_to(drone, lowest_distance_bottle["latitude"], lowest_distance_bottle["longitude"], 80, 0)
            #await airdrop.drop_bottle(lowest_distance_bottle)
            await asyncio.wait(5)
            bottle_locations.pop(bottle_num)

        return Land(self.state_settings)
    
    async def get_distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

if __name__ == "__main__":

    # Init drone
    drone = System()
    asyncio.ensure_future(drone.connect(system_address="udp://:14540"))

    # Init state
    state = AirDrop()

    # Run state
    asyncio.ensure_future(state.run(drone))

    # Run the event loop until the program is canceled with e.g. CTRL-C
    asyncio.get_event_loop().run_forever()
