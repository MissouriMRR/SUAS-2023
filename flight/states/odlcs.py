"""Fly througn ODLC search area and search for all 5 objects"""

from mavsdk import System
from flight.states.state import State
from flight.states.airdrop import AirDrop
from flight.odlc_boundaries.execute import move_to
from mavsdk.camera import Mode
import logging

class ODLC(State):
    """
    State to fly through ODLC search grid and scan for standard & emergent objects

    Methods
    -------
    run(drone: System) -> AirDrop
        Run ODLC flight algorithm and pass to next state
    """

    async def run(self, drone: System) -> AirDrop:
        """
        Fly through the ODLC search area and look for the 5 standard objects and emergent object

        Parameters
        ----------
        drone : System
            MAVSDK drone object to manipulate drone position & attitude

        Returns
        -------
        AirDrop : State
            The next state in the state machine, AirDrop for the payloads
        """

        #Camera gets ready to take photos
        await drone.camera.set_mode(Mode.PHOTO)
        logging.info("Camera changed to Photo mode")

        #These waypoint values are all that are needed to traverse the whole odlc drop location because it is a small rectangle
        #The first waypoint is the midpoint of the left side of the rectangle(one of the short sides), the second point is the
        #midpoint of the right side of the rectangle(other short side), and the third point is the top left corner of the rectangle
        #it goes there for knowing where the drone ends to travel to each of the drop locations, the altitude is locked at 85 because
        #we want the drone to stay level and the camera to view the whole odlc boundary
        waypoint: dict[str, list[float]] = {
        "lats": [38.31451966813249, 38.31430872867596, 38.31461622313521],
        "longs": [-76.54519982319357, -76.54397320409971, -76.54516993186949],
        "Altitude": [85],
        }

        #traverses the 3 waypoints starting at the midpoint on left to midpoint on the right then to the top left corner at the rectangle
        point: int
        logging.info("Starting odlc zone flyover")
        for point in range(3):
            if(point == 0):
                logging.info("Moving to the center of the west boundary")
            elif(point == 1):
                await drone.camera.start_photo_interval(5)
                logging.info("Moving to the center of the east boundary")
            elif(point == 2):
                logging.info("Moving to the north west corner")

            await move_to(
                drone, waypoint["lats"][point], waypoint["longs"][point], waypoint["Altitude"][0]
            )
            await drone.camera.stop_photo_interval()
        return AirDrop(self.state_settings)