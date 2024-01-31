"""
This module contains the implementation of a state machine and a kill switch
to test them in a simulated or real-world environment. It includes functionality
to check waypoints and ensure the drone remains within predefined boundaries.

Classes
-------
BoundaryPoint
    A point defining a boundary for the drone's operation.

Functions
---------
in_bounds(boundary, latitude, longitude, altitude)
    Checks if a given point is within a specified boundary.

waypoint_check(drone, _sim)
    Verifies if a drone reaches each waypoint in a predefined path.

run_test(_sim)
    Initializes the state machine and starts the waypoint check.

"""
import asyncio
import logging
from mavsdk import System
from flight.extract_gps import BoundaryPoint, GPSData, extract_gps
from flight.extract_gps import Waypoint as Waylist

from state_machine.flight_manager import FlightManager


SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board
GPS_PATH: str = "flight/data/waypoint_data.json"


async def in_bounds(
    boundary: list[BoundaryPoint], latitude: float, longitude: float, altitude: float
) -> bool:
    """
    Determines if a point specified by latitude, longitude, and altitude
    is inside a given boundary.

    Parameters
    ----------
    boundary : list of BoundaryPoint
        A list of boundary points defining a closed polygonal area.
    latitude : float
        The latitude of the point to check.
    longitude : float
        The longitude of the point to check.
    altitude : float
        The altitude of the point to check.

    Returns
    -------
    bool
        True if the point is inside the boundary, False otherwise.
    """
    if altitude < 75 or altitude > 750:
        return False
    num: int = len(boundary)
    j: int = num - 1
    inside: bool = False

    for i in range(num):
        lat_i: float = boundary[i][0]
        long_i: float = boundary[i][1]
        lat_j: float = boundary[j][0]
        long_j: float = boundary[j][1]

        if ((long_i > longitude) != (long_j > longitude)) and (
            latitude < (lat_j - lat_i) * (longitude - long_i) / (long_j - long_i) + lat_i
        ):
            inside = not inside

        j = i

    return inside


async def waypoint_check(drone: System, _sim: bool = True) -> None:
    """
    Checks if the drone reaches each waypoint in a list and remains
    within the specified boundary during its flight.

    Parameters
    ----------
    drone : System
        The drone system object from mavsdk.
    _sim : bool, optional
        Specifies whether the function is being run in a simulation mode (default is True).
    """

    gps_dict: GPSData = extract_gps(GPS_PATH)
    waypoints: list[Waylist] = gps_dict["waypoints"]
    boundary: list[BoundaryPoint] = gps_dict["boundary_points"]
    current_waypoint: int = 1
    for waypoint in waypoints:
        reached: bool = False
        while not reached:
            async for position in drone.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

                # checks if drone's location is within boundary
                if not await in_bounds(boundary, drone_lat, drone_long, drone_alt):
                    logging.info("Out of bounds!")
                    break

                #  accurately checks if location is reached and
                #  stops for 15 secs and then moves on.
                if (
                    (round(drone_lat, 5) == round(waypoint[0], 5))
                    and (round(drone_long, 5) == round(waypoint[1], 5))
                    and (round(drone_alt, 1) == round(waypoint[2], 1))
                ):
                    reached = True
                    break
        logging.info("Waypoint %d reached.", current_waypoint)
        current_waypoint += 1


async def run_test(_sim: bool) -> None:  # Temporary fix for unused variable
    """
    Initialize and run the flight manager and waypoint check for testing
    the state machine in either simulated or real-world mode.

    Parameters
    ----------
    _sim : bool
        Specifies whether to run the state machine in simulation mode.
    """
    flight_manager: FlightManager = FlightManager()
    flight_manager.start_manager(_sim)

    await waypoint_check(flight_manager.drone.system)


if __name__ == "__main__":
    asyncio.run(run_test(True))
