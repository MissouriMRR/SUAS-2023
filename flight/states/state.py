"""Base state class for competition stages"""

# pylint: disable=abstract-method
# NOTE: For the run() method of state

import asyncio
import logging

from math import sqrt
from mavsdk import System, telemetry

import flight.config

from flight.state_settings import StateSettings
from flight.waypoint.goto import move_to
from flight.extract_gps import extract_gps, Waypoint, GPSData
from flight.maestro.air_drop import AirdropControl


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

    get_distance(x1: float, y1: float, x2: float, y2: float) -> float
        Gets the distance between two points
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
        # TODO: Stop this
        # Using sample locations for now
        bottle_locations = {
            1: {"latitude": 37.901096681, "longitude": -91.6658804},
            2: {"latitude": 37.9009907274, "longitude": -91.66255949},
            3: {"latitude": 37.89915707, "longitude": -91.663931618},
            4: {"latitude": 37.89783936, "longitude": -91.661258865},
            5: {"latitude": 37.900769059, "longitude": -91.665224920},
        }

        # setup airdrop
        airdrop = AirdropControl()

        # For the amount of bottles there are...
        for num in range(len(bottle_locations)):
            logging.info("Bottle drop #", num + 1, "started")
            # Set initial value for lowest distance so we can compare
            lowest_distance: float = 100000
            bottle_num: int
            # Get the drones current position
            async for position in drone.telemetry.position():
                current_location: telemetry.Position = position
                break
            # For each bottle location, get the distance from the drone
            for location in bottle_locations.values():
                distance: float = await self.get_distance(
                    current_location.latitude_deg,
                    current_location.longitude_deg,
                    location["latitude"],
                    location["longitude"],
                )
                if distance < lowest_distance:
                    lowest_distance = distance
                    bottle_loc: dict[str, float] = location
                    bottle_num = [i for i in bottle_locations if bottle_locations[i] == location][0]
            logging.info(
                f'Nearest bottle: #{bottle_num} at ({bottle_loc["latitude"]}, {bottle_loc["longitude"]})'
            )
            # Move to the nearest bottle
            await move_to(drone, bottle_loc["latitude"], bottle_loc["longitude"], 80, 1)
            await airdrop.drop_bottle(bottle_num)
            await asyncio.sleep(
                5
            )  # This will need to be changed based on how long it takes to drop the bottle
            # Remove the bottle location from the dictionary
            bottle_locations.pop(bottle_num)
        logging.info("-- Airdrop done!")
        return Land(self.state_settings)

    async def get_distance(self, x_1: float, y_1: float, x_2: float, y_2: float) -> float:
        """
        Gets the distance between two points

        Parameters
        ----------
        x_1 : float
            The x coordinate of the first point
        y_1 : float
            The y coordinate of the first point
        x_2 : float
            The x coordinate of the second point
        y_2 : float
            The y coordinate of the second point

        Returns
        -------
        float
            The distance between the two points
        """
        return sqrt((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2)


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
