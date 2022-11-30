"""
Functions for generating search paths to cover an area for finding the standard odlc objects
"""

from typing import List, Dict, Tuple, Union
from shapely.geometry import Polygon
import utm
import plotter
from execute import move_to
from mavsdk import System
import logging
import asyncio


def latlon_to_utm(coords: Dict[str, Union[float, int, str]]) -> Dict[str, Union[float, int, str]]:
    """Converts latlon coordinates to utm coordinates and adds the data to the dictionary

    Parameters
    ----------
    coords : Dict[str, float]
        A dictionary containing lat long coordinates

    Returns
    -------
    Dict[str, float]
        An updated dictionary with additional keys and values with utm data
    """

    utm_coords: Tuple[float, float, int, str] = utm.from_latlon(
        coords["latitude"], coords["longitude"]
    )
    coords["utm_x"] = utm_coords[0]
    coords["utm_y"] = utm_coords[1]
    coords["utm_zone_number"] = utm_coords[2]
    coords["utm_zone_letter"] = utm_coords[3]
    return coords


def all_latlon_to_utm(
    list_of_coords: List[Dict[str, Union[float, int, str]]]
) -> List[Dict[str, Union[float, int, str]]]:
    """Converts a list of dictionaries with latlon data to add utm data

    Parameters
    ----------
    list_of_coords : List[Dict[str, Union[float, int, str]]]
        A list of dictionaries that contain lat long data

    Returns
    -------
    List[Dict[str, Union[float, int, str]]]
        An updated list of dictionaries with added utm data
    """

    for i, _ in enumerate(list_of_coords):
        list_of_coords[i] = latlon_to_utm(list_of_coords[i])
    return list_of_coords


def generate_search_paths(
    d_search_area_boundary: List[Dict[str, float]], buffer_distance: int
) -> List[Tuple[float, float]]:
    """Generates a list of search paths of increasingly smaller sizes until the whole area
    of the original shape has been covered

    Parameters
    ----------
    d_search_area_boundary : List[Dict[str, float]]]
        A list of coordinates in dictionary form that contain utm coordinate data
    buffer_distance : int
        The distance that each search path will be apart from the previous one.
        For complete photographic coverage of the area, this should be equal to half the height
        of the area the camera covers on the ground given the current altitude.

    Returns
    -------
    List[Tuple[float, float]]
        A list of concentric search paths that cover the area of the polygon
    """

    # convert to shapely polygon for buffer operations
    search_area_points: List[Tuple[float, float]] = [
        (point["utm_x"], point["utm_y"]) for point in d_search_area_boundary
    ]
    boundary_shape: Polygon = Polygon(search_area_points)

    generated_search_paths = [] #: List[List[Tuple[float, float]]

    # shrink boundary by a fixed amount until the area it covers is 0
    # add the smaller boundary to our list of search paths on each iteration
    while boundary_shape.area > 0:
        # print(boundary_shape.exterior.coords.xy)
        generated_search_paths.append(
            tuple(zip(*boundary_shape.exterior.coords.xy))  # pylint: disable=maybe-no-member
        )
        boundary_shape = boundary_shape.buffer(buffer_distance, single_sided=True)

    return generated_search_paths

async def run() -> None:
    """
    This function is just a driver to test the goto function and runs through the
    entire waypoint section of the SUAS competition
    """

    Waypoint: dict[list[float], list[float], float] = {"lats": [37.94919790623559, 37.94862722088389, 37.94949210234766], "longs": [-91.78473191296871, -91.78302701112852, -91.78461752885457], "Altitude": 85}


    #create a drone object
    drone: System = System()
    await drone.connect(system_address="udp://:14540")

    #initilize drone configurations
    await drone.action.set_takeoff_altitude(12)
    await drone.action.set_maximum_speed(20)

    #connect to the drone
    logging.info("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Drone discovered!")
            break

    logging.info("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            logging.info("Global position estimate ok")
            break

    logging.info("-- Arming")
    await drone.action.arm()

    logging.info("-- Taking off")
    await drone.action.takeoff()

    #wait for drone to take off
    await asyncio.sleep(10)

    #move to each waypoint in mission
    for point in range(3):
        await move_to(drone,Waypoint["lats"][point],Waypoint["longs"][point],85,True)

    #return home
    # logging.info("Last waypoint reached")
    # logging.info("Returning to home")
    # await drone.action.return_to_launch()
    # print("Staying connected, press Ctrl-C to exit")

    #infinite loop till forced disconnect
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
   # data_search_area_boundary: List[Dict[str, float]] = [
    #    {"latitude": 38.31442311312976, "longitude": -76.54522971451763},
    #    {"latitude": 38.31421041772561, "longitude": -76.54400246436776},
    #    {"latitude": 38.3144070396263, "longitude": -76.54394394383165},
    #    {"latitude": 38.31461622313521,"longitude": -76.54516993186949},
    #    {"latitude": 38.31442311312976, "longitude": -76.54522971451763},
    # ]

 

    data_search_area_boundary: List[Dict[str, float]] = [
        {"latitude": 37.94949210234766, "longitude": -91.78461752885457,}, # Top Left Corner
        {"latitude": 37.94890371012351, "longitude": -91.78484629708285,}, # Bottom Left Corner
        {"latitude": 37.94824920904741, "longitude": -91.78307727392504,}, # Bottom Right Corner
        {"latitude": 37.94900523272037, "longitude": -91.782976748332,}, # Top Right Corner
        {"latitude": 37.94949210234766, "longitude": -91.78461752885457,}, # Top Left Corner
        {"latitude": 37.94919790623559, "longitude": -91.78473191296871}, # Left Midpoint
        {"latitude": 37.94862722088389, "longitude": -91.78302701112852}, # Right Midpoint
    ]

    drone: System = System()


    # algorithm
    # (2 coordinates for side 1) / 2 = starting point
    # (2 coordinates for opposite side) / 2 = ending coordinate
    # altitude = get_altitude_for_odlc(width, focal_length)
    # altitude = 75 if altitude < 75 else altitude
    # set drone height to altitude
    # fly between starting and ending coordinates, this should fly it length wise
    # run video camera the whole time recording data about odlc positions -- vision task?


    # Add utm coordinates to all
    data_search_area_boundary_utm: Dict[str, Union[float, int, str]] = all_latlon_to_utm(
        data_search_area_boundary
    )

    # Generate search path
    BUFFER_DISTANCE: int = -40 # use height/2 of camera image area on ground as buffer distance
    search_paths = generate_search_paths(data_search_area_boundary_utm, BUFFER_DISTANCE)

    print(search_paths)

    asyncio.run(run())

    # fly all points in search_paths[0],
    # when you reach your starting point,
    # fly all points in search_paths[1],
    # etc... until all search paths have been flown

    # Plot data
    plotter.plot(search_paths)
