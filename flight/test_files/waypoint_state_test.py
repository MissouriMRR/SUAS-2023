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
import math
import time
import sys
from typing import Final

from mavsdk import System
import utm

from flight.extract_gps import BoundaryPoint, GPSData, extract_gps
from flight.extract_gps import Waypoint as Waylist
from state_machine.flight_manager import FlightManager


SIM_ADDR: Final[str] = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: Final[str] = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board

# 3.28084 feet per meter
CLOSE_THRESHOLD: Final[float] = (
    15 / 3.28084
)  # How close the drone should get to each waypoint, in meters


def in_bounds(
    boundary: list[BoundaryPoint],
    latitude: float,
    longitude: float,
    altitude: float,
    min_altitude: float,
    max_altitude: float,
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
        The altitude of the point to check, in meters.
    min_altitude : float
        The minimum allowed altitude, in meters.
    max_altitude : float
        The maximum allowed altitude, in meters.

    Returns
    -------
    bool
        True if the point is inside the boundary, False otherwise.
    """
    if not min_altitude <= altitude <= max_altitude:
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


def calculate_distance(
    lat_deg_1: float,
    lon_deg_1: float,
    altitude_m_1: float,
    lat_deg_2: float,
    lon_deg_2: float,
    altitude_m_2: float,
) -> float:
    """
    Calculate the distance, in meters, between two coordinates

    Parameters
    ----------
    lat_deg_1 : float
        The latitude, in degrees, of the first coordinate.
    lon_deg_1 : float
        The longitude, in degrees, of the first coordinate.
    altitude_m_1 : float
        The altitude, in meters, of the first coordinate.
    lat_deg_2 : float
        The latitude, in degrees, of the second coordinate.
    lon_deg_2 : float
        The longitude, in degrees, of the second coordinate.
    altitude_m_2 : float
        The altitude, in meters, of the second coordinate.

    Returns
    -------
    float
        The distance between the two coordinates.
    """
    easting_2: float
    northing_2: float
    zone_num_2: int
    zone_letter_2: str
    easting_2, northing_2, zone_num_2, zone_letter_2 = utm.from_latlon(lat_deg_2, lon_deg_2)
    easting_1: float
    northing_1: float
    easting_1, northing_1, _, _ = utm.from_latlon(
        lat_deg_1,
        lon_deg_1,
        force_zone_number=zone_num_2,
        force_zone_letter=zone_letter_2,
    )

    return math.hypot(
        easting_1 - easting_2,
        northing_1 - northing_2,
        altitude_m_1 - altitude_m_2,
    )


async def waypoint_check(drone: System, _sim: bool, path_data_path: str) -> None:
    """
    Checks if the drone reaches each waypoint in a list and remains
    within the specified boundary during its flight.

    Parameters
    ----------
    drone : System
        The drone system object from mavsdk.
    _sim : bool
        Specifies whether the function is being run in a simulation mode.
    path_data_path : str
        The path to the JSON file containing the boundary and waypoint data.
    """
    gps_dict: GPSData = extract_gps(path_data_path)
    waypoints: list[Waylist] = gps_dict["waypoints"]
    boundary: list[BoundaryPoint] = gps_dict["boundary_points"]
    # 3.28084 ft per m
    min_altitude: float = gps_dict["altitude_limits"][0] / 3.28084
    max_altitude: float = gps_dict["altitude_limits"][1] / 3.28084

    previously_out_of_bounds: bool = False
    previous_log_time: float = time.perf_counter()  # time.perf_counter() is monotonic
    for waypoint_num, waypoint in enumerate(waypoints):
        async for position in drone.telemetry.position():
            # continuously checks current latitude, longitude and altitude of the drone
            drone_lat: float = position.latitude_deg
            drone_lon: float = position.longitude_deg
            drone_alt: float = position.relative_altitude_m

            # checks if drone's location is within boundary
            if not in_bounds(boundary, drone_lat, drone_lon, drone_alt, min_altitude, max_altitude):
                if not previously_out_of_bounds:
                    logging.info("(Waypoint State Test) Out of bounds!")
                    previously_out_of_bounds = True
            else:
                if previously_out_of_bounds:
                    logging.info("(Waypoint State Test) Re-entered bounds.")
                    previously_out_of_bounds = False

            distance_to_waypoint: float = calculate_distance(
                drone_lat, drone_lon, drone_alt, *waypoint
            )

            # accurately checks if location is reached
            if distance_to_waypoint < CLOSE_THRESHOLD:
                break

            curr_time: float = time.perf_counter()
            if curr_time - previous_log_time >= 1.0:
                logging.info("(Waypoint State Test) %f m to waypoint", distance_to_waypoint)
                previous_log_time = curr_time

        logging.info("(Waypoint State Test) Waypoint %d reached.", waypoint_num)


async def run_test(_sim: bool) -> None:  # Temporary fix for unused variable
    """
    Initialize and run the flight manager and waypoint check for testing
    the state machine in either simulated or real-world mode.

    Parameters
    ----------
    _sim : bool
        Specifies whether to run the state machine in simulation mode.
    """
    # Output logging info to stdout
    logging.basicConfig(filename="/dev/stdout", level=logging.INFO)

    path_data_path: str = "flight/data/waypoint_data.json" if _sim else "flight/data/golf_data.json"

    flight_manager: FlightManager = FlightManager()
    asyncio.ensure_future(waypoint_check(flight_manager.drone.system, _sim, path_data_path))
    flight_manager.run_manager(_sim, path_data_path)


if __name__ == "__main__":
    print("Pass argument --sim to enable the simulation flag.")
    print("When the simulation flag is not set, golf data is used for the boundary and waypoints.")
    print()
    asyncio.run(run_test("--sim" in sys.argv))
