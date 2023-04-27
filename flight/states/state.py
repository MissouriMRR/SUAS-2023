"""Base state class for competition stages"""

# pylint: disable=abstract-method
# NOTE: For the run() method of state

import asyncio
import json
import logging
import time

from mavsdk import System

from libsonyapi.camera import Camera
from libsonyapi.actions import Actions

import flight.config

from flight.state_settings import StateSettings
from flight.waypoint.goto import move_to
from flight.extract_gps import extract_gps, Waypoint, GPSData


class State:
    """
    Base flight state class

    Attributes
    ----------
    state_settings : StateSettings
        Parameters of flight plan, i.e. title description, etc.

    Methods
    -------
    run(drone: System) -> None
        Runs the code for each state and return the next, or None if at the end of the state machine
        For the base class, NotImplementedError is raised
    check_arm_or_arm(drone: System) -> None
        Verifies if drone is armed, and if not, arms it
    """

    def __init__(self, state_settings: StateSettings) -> None:
        """
        Initializes base state with mission's Settings

        Parameters
        ----------
        state_settings : StateSettings
            Flight mission attributes & competition data
        """
        logging.info("State %s has begun", self.name)
        self.state_settings: StateSettings = state_settings

    async def run(
        self, drone: System
    ) -> Start | PreProcess | Takeoff | Waypoints | ODLC | AirDrop | Land | Final | None:
        """
        Flight mission code for each state

        Parameters
        ----------
        drone : System
            MAVSDK drone object used to manipulate drone position & attitude

        Raises
        ------
        NotImplementedError
            Since this is the base State class, this run() function should not be utilized.
        """
        raise NotImplementedError("Base class function should not be called.")

    async def check_arm_or_arm(self, drone: System) -> None:
        """
        Determines if drone has armed, and if not, proceeds to arm it

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position & attitude
        """
        async for is_armed in drone.telemetry.armed():
            if not is_armed:
                logging.debug("Drone not armed. Attempting to arm...")
                await drone.action.arm()
            else:
                logging.warning("Drone armed.")
                break

    @property
    def name(self) -> str:
        """
        Getter function to return name & type of state

        Returns
        -------
        name : State
            Name of current state
        """
        return type(self).__name__


class AirDrop(State):
    """
    State to fly to each drop location and release the payloads to the corresponding standard object

    Methods
    -------
    run(drone: System) -> Land | ODLC
        Maneuver drone to each drop location and release
        the payloads onto corresponding standard ODLC
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
        return Land(self.state_settings)


class Final(State):
    """
    Last state in the state machine to end the competition code

    Methods
    -------
    run(drone: System) -> None
        Does nothing and ends state machine
    """

    async def run(self, drone: System) -> None:
        """
        Do nothing state to log end of competition code and terminate state machine

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude
        """
        logging.debug("End of state machine.")


class Land(State):
    """
    State to safely land the drone after other SUAS objectives have been finished

    Methods
    -------
    run(drone: System) -> Final
        Land the drone safely from operational altitude
    """

    async def run(self, drone: System) -> Final:
        """
        Maneuver the drone to the landing location and safely land the drone

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        Final : State
            Last state to end state machine
        """
        logging.debug("Drone returning to launch position...")
        await drone.action.return_to_launch()
        logging.debug("Drone landed.")
        return Final(self.state_settings)


class ODLC(State):
    """
    State to fly through ODLC search grid and scan for standard & emergent objects

    Methods
    -------
    picture_gps(self, drone:System) -> None
        starts taking pictures with the camera and stores them with sonylib api
        !!not tested or confirmed to work!!
        and puts the locations and file name in a file for vision and once all
        airdrop locations are found stops taking photos and exits
    airdrop_count(self) -> int
        counts number of airdrops found and returns it
    run(drone: System) -> AirDrop
        Run ODLC flight algorithm and pass to next state
    """

    async def picture_gps(self, drone: System) -> None:
        """
        Starts taking photos using the camera that is initialized
        gets the pictures name and drone information and puts that information
        into a file for vision to use and once all airdrop locations are found
        stops taking photos and exits the function

        Preconditions
        -------------
        No photos in the camera storage

        Parameters
        ----------
        drone: System
            a drone object that has all offboard data needed for computation

        """
        take_photos: bool = True
        pic: int = 1
        info: dict[str, dict[str, int | list[int | float] | float]] = {}
        # Camera gets ready to take photos
        camera: Camera = Camera()
        logging.info("Camera initialized and starting to take photos")
        while take_photos:
            camera.do(Actions.actTakePicture)
            if 100 > pic % 10 > 9:
                name = f"DSC000{pic}.jpg"
            else:
                name = f"DSC0000{pic}.jpg"

            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

            point: dict[str, dict[str, int | list[int | float] | float]] = {
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

            with open("camera.json", "w", encoding="ascii") as camera:
                json.dump(info, camera)

            with open("state.txt", "r", encoding="ascii") as state:
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

        with open("flight/data/output.json", encoding="ascii") as output:
            airdrop_dict = json.load(output)
            airdrops = len(airdrop_dict)
        return airdrops

    async def run(self, drone: System) -> AirDrop:
        """
        Fly through the ODLC search area and look for the 5 standard objects
        and emergent object and starts the timelapse photo for the region

        Parameters
        ----------
        drone : System
            MAVSDK drone object to manipulate drone position & attitude

        Returns
        -------
        AirDrop : State
            The next state in the state machine, AirDrop for the payloads
        """

        # These waypoint values are all that are needed to traverse the whole odlc drop location
        # because it is a small rectangle
        # The first waypoint is the midpoint of
        # the left side of the rectangle(one of the short sides), the second point is the
        # midpoint of the right side of the rectangle(other short side),
        # and the third point is the top left corner of the rectangle
        # it goes there for knowing where the drone ends to travel to each of the drop locations,
        # the altitude is locked at 100 because
        # we want the drone to stay level and the camera to view the whole odlc boundary
        # the altitude 100 feet was chosen to cover the whole odlc boundary
        # because the boundary is 70ft by 360ft the fov of the camera
        # is vertical 52.1 degrees and horizontal 72.5,
        # so using the minimum length side of the photo the coverage would be 90 feet allowing
        # 10 feet overlap on both sides
        waypoint: dict[str, list[float]] = {
            "lats": [38.31451966813249, 38.31430872867596, 38.31461622313521],
            "longs": [-76.54519982319357, -76.54397320409971, -76.54516993186949],
            "Altitude": [100],
        }

        # traverses the 3 waypoints starting at the midpoint on left to midpoint on the right
        # then to the top left corner at the rectangle
        point: int
        airdrops: int = 0
        while airdrops != 5:
            point = 0
            logging.info("Starting odlc zone flyover")
            for point in range(3):
                if point == 0:
                    logging.info("Moving to the center of the west boundary")
                elif point == 1:
                    # starts taking photos at a .5 second interval because we want
                    # to get multiple photos of the boundary so there is overlap and
                    # the speed of the drone should be 20 m/s which is 64 feet/s which means
                    # it will traverse the length of the boundary (360 ft) in 6 sec
                    # and that means with the shortest length of photos
                    #  being taken depending on rotation
                    # would be 90 feet and we want to take multiple photos
                    # so we would need a minimum of 4 photos to cover
                    #  the whole boundary and we want multiple,
                    # so using .5 seconds between each photo allows
                    # it to take a minimum of 12 photos of
                    #  the odlc boundary which will capture the whole area
                    await self.picture_gps(drone)
                    logging.info("Moving to the center of the east boundary")
                elif point == 2:
                    logging.info("Moving to the north west corner")

                await move_to(
                    drone,
                    waypoint["lats"][point],
                    waypoint["longs"][point],
                    waypoint["Altitude"][0],
                    2 / 3,
                )
            airdrops = await self.airdrop_count()

        with open("flight/data/state.txt", "w", encoding="ascii") as state:
            state.write("true")
        # stops taking photos
        return AirDrop(self.state_settings)


class PreProcess(State):
    """
    State to generate flight paths for competition

    Methods
    -------
    run(drone: System) -> Takeoff
        Generate an in-bounds flight path from the given GPS data
    """

    async def run(self, drone: System) -> Takeoff:
        """
        Given GPS coordinates of boundary & waypoints, create efficient flight path

        Parameters
        ----------
        drone : System
            MAVSDK object used to access and manipulate drone operations

        Returns
        -------
        Takeoff : State
            Next state to lift drone off the ground
        """
        return Takeoff(self.state_settings)


class Start(State):
    """
    Preliminary state to initiate state machine

    Methods
    -------
    begin(drone: System) -> PreProcess
        Start the state machine & proceed to PreProcess state
    """

    async def begin(self, drone: System) -> PreProcess:  # pylint: disable=unused-argument
        """
        Start state machine and pass to PreProcess state

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        PreProcess : State
            Next state to generate flight paths
        """
        logging.debug("Start state machine")
        return PreProcess(self.state_settings)


class Takeoff(State):
    """
    Runs takeoff procedure to lift the drone to preset altitude

    Methods
    -------
    run(drone: System) -> Waypoints
        Lift the drone from takeoff location and begin movement to first waypoint
    """

    async def run(self, drone: System) -> Waypoints:
        """
        Run takeoff procedure to move drone upwards using offboard or action functions

        Parameters
        ----------
        drone : System
            MAVSDK object to manipulate drone position and attitude

        Returns
        -------
        Waypoints : State
            Next state to fly waypoint path
        """
        # Initialize altitude (convert feet to meters)
        await drone.action.set_takeoff_altitude(flight.config.TAKEOFF_ALT / 3.2808)

        # Arm drone and takeoff
        logging.info("Arming Drone")
        await drone.action.arm()

        logging.info("Taking off")
        await drone.action.takeoff()

        # Wait for drone to take off
        await asyncio.sleep(2)

        # Go to Waypoint State
        return Waypoints(self.state_settings)


class Waypoints(State):
    """
    State to run through waypoint flight path

    Methods
    -------
    run(drone: System) -> ODLC
        Process set of waypoints and fly within 25ft of each
    """

    async def run(self, drone: System) -> ODLC:
        """
        Run through list of waypoints & fly within 25ft of each desired point

        Parameters
        ----------
        drone : System
            MAVSDK object for manipulating drone position & attitude

        Returns
        -------
        ODLC : State
            Re-fly the waypoints if we failed to reach a waypoint boundary,
            or progress to ODLC flight stage
        """
        gps_dict: GPSData = extract_gps("flight/data/waypoint_data.json")
        waypoints: list[Waypoint] = gps_dict["waypoints"]

        for waypoint in waypoints:
            # 5/6 is the fast parameter to make it less accurate to within 3.6 feet
            # so it can fly through the waypoints faster
            await move_to(drone, waypoint[0], waypoint[1], waypoint[2], 5 / 6)

        return ODLC(self.state_settings)
