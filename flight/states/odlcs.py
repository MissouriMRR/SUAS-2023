"""Fly througn ODLC search area and search for all 5 objects"""

from mavsdk import System
from flight.states.state import State
from flight.maestro.air_drop import AirDrop
from flight.odlc_boundaries.execute import move_to
import logging
import json
import time
from libsonyapi.camera import Camera
from libsonyapi.actions import Actions


class ODLC(State):
    """
    State to fly through ODLC search grid and scan for standard & emergent objects, and start timelapse photo of region

    Methods
    -------
    run(drone: System) -> AirDrop
        Run ODLC flight algorithm and pass to next state
    """

    async def picture_gps(self, drone) -> None:
        take_photos: bool = True
        pic: int = 1
        info: dict = {}
        while take_photos:
            camera.do(Actions.actTakePicture)
            if 100 > pic % 10 > 9:
                name = "DSC000" + pic + ".jpg"
            else:
                name = "DSC0000" + pic + ".jpg"

            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

            point: dict = {
                name: {
                    "focal_length": 14,
                    "rotation_deg": [
                        drone.offboard.Attitude.roll_deg,
                        drone.offboard.Attitude.pitch_deg,
                        drone.offboard.Attitude.yaw_deg,
                    ],
                    "drone_coordinates": [drone_lat, drone_long],
                    "altitude_f": drone_alt,
                }
            }

            info.update(point)

            with open("camera.json", "w") as camera:
                json.dump(info, camera)

            with open("state.txt", "r") as state:
                if state.read() == "true":
                    take_photos = False
            time.sleep(0.5)
            pic = pic + 1

    async def airdrop_count(self) -> int:
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
        camera = Camera()
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
                    await self.picture_gps()
                    logging.info("Moving to the center of the east boundary")
                elif point == 2:
                    logging.info("Moving to the north west corner")

                await move_to(
                    drone,
                    waypoint["lats"][point],
                    waypoint["longs"][point],
                    waypoint["Altitude"][0],
                )
            airdrops = await self.airdrop_count()

        with open("flight/data/state.txt", "w") as state:
            state.write("true")
        # stops taking photos
        return AirDrop(self.state_settings)
