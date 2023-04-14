"""Fly througn ODLC search area and search for all 5 objects"""

from mavsdk import System
from flight.states.state import State
from flight.states.airdrop import AirDrop
from flight.odlc_boundaries.execute import move_to
from mavsdk.camera import Mode
import logging
import json


class ODLC(State):
    """
    State to fly through ODLC search grid and scan for standard & emergent objects, and start timelapse photo of region

    Methods
    -------
    run(drone: System) -> AirDrop
        Run ODLC flight algorithm and pass to next state
    """

    async def airdrop_count() -> int:
        """
        Counts the number of airdrop locations found and returns it
        
        Parameters
        ----------
        None

        Returns
        -------
        airdrop: int
            The amount of airdrops found
        """
        
        with open("flight/data/output.json") as output:
            airdrop_dict = json.load(output)
            airdrops = len(airdrop_dict)
        return airdrops

    async def run(self, drone: System) -> AirDrop:
        """
        Fly through the ODLC search area and look for the 5 standard objects and emergent object and starts the timelapse photo for the region

        Parameters
        ----------
        drone : System
            MAVSDK drone object to manipulate drone position & attitude

        Returns
        -------
        AirDrop : State
            The next state in the state machine, AirDrop for the payloads
        """

        # Camera gets ready to take photos
        await drone.camera.set_mode(Mode.PHOTO)
        logging.info("Camera changed to Photo mode")

        # These waypoint values are all that are needed to traverse the whole odlc drop location because it is a small rectangle
        # The first waypoint is the midpoint of the left side of the rectangle(one of the short sides), the second point is the
        # midpoint of the right side of the rectangle(other short side), and the third point is the top left corner of the rectangle
        # it goes there for knowing where the drone ends to travel to each of the drop locations, the altitude is locked at 100 because
        # we want the drone to stay level and the camera to view the whole odlc boundary
        # the altitude 100 feet was chosen to cover the whole odlc boundary because the boundary is 70ft by 360ft the fov of the camera
        # is vertical 52.1 degrees and horizontal 72.5, so using the minimum length side of the photo the coverage would be 90 feet allowing
        # 10 feet overlap on both sides
        waypoint: dict[str, list[float]] = {
            "lats": [38.31451966813249, 38.31430872867596, 38.31461622313521],
            "longs": [-76.54519982319357, -76.54397320409971, -76.54516993186949],
            "Altitude": [100],
        }

        # traverses the 3 waypoints starting at the midpoint on left to midpoint on the right then to the top left corner at the rectangle
        point: int
        airdrops: int
        while airdrops != 5:
            point = 0
            logging.info("Starting odlc zone flyover")
            for point in range(3):
                if point == 0:
                    logging.info("Moving to the center of the west boundary")
                elif point == 1:
                    # starts taking photos at a .5 second interval because we want to get multiple photos of the boundary so there is overlap and
                    # the speed of the drone should be 20 m/s which is 64 feet/s which means it will traverse the length of the boundary (360 ft) in 6 sec
                    # and that means with the shortest length of photos being taken depending on rotation would be 90 feet and we want to take multiple photos
                    # so we would need a minimum of 4 photos to cover the whole boundary and we want multiple, so using .5 seconds between each photo allows
                    # it to take a minimum of 12 photos of the odlc boundary which will capture the whole area
                    await drone.camera.start_photo_interval(0.5)
                    logging.info("Moving to the center of the east boundary")
                elif point == 2:
                    logging.info("Moving to the north west corner")

                await move_to(
                    drone,
                    waypoint["lats"][point],
                    waypoint["longs"][point],
                    waypoint["Altitude"][0],
                )
            airdrops = await airdrop_count()

        with open("flight/data/state.txt", "w") as state:
            state.write("true")
        # stops taking photos
        await drone.camera.stop_photo_interval()
        return AirDrop(self.state_settings)
