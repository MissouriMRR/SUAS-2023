"""Fly to each AirDrop location and release the payloads"""

from mavsdk import System
from flight.states.state import State
from flight.states.odlcs import ODLC
from flight.states.land import Land

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

        # Vision guys will give a dict using this format for the bottle locations:
        # bottle_dict : {
        #   0: ["latitude": 1, "longitude": 2],
        #   1: ...,
        # }
        # We will use a sample one for now!
        bottle_locations = {
            0: {"latitude": 1, "longitude": 1},
            1: {"latitude": 1, "longitude": 1},
            2: {"latitude": 1, "longitude": 1},
            3: {"latitude": 1, "longitude": 1},
            4: {"latitude": 1, "longitude": 1},
        }

        for location in bottle_locations:
            print(location)


        return Land(self.state_settings)

if __name__ == "__main__":

    drone: System = System()

    AirDrop.run(drone)
