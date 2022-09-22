"""
Contains the extract_gps() function for extracting data out of
the provided waypoint data JSON file for the SUAS competition.
"""
from collections import namedtuple
from typing import Any, List, NamedTuple
import json
from typing_extensions import TypedDict

GPSData = TypedDict(
    "GPSData",
    {
        "waypoints": List[NamedTuple],
        "boundary_points": List[NamedTuple],
        "altitude_limits": List[int],
    },
)


def extract_gps(path: str) -> GPSData:
    """
    Returns the waypoints, boundary points, and altitude limits from a waypoint data file.

    Parameters
    ----------
    path : str
        File path to the waypoint data JSON file.

    Returns
    -------
    GPSData : TypedDict[list[NamedTuple[int, int, int]], list[NamedTuple[int, int]], list[int, int]]
        The data in the waypoint data file
        waypoints : list[NamedTuple[int, int, int]]
            Waypoint : NamedTuple[int, int, int]
                latitude : int
                    The latitude of the waypoint.
                longitude : int
                    The longitude of the waypoint.
                altitude : int
                    The altitude of the waypoint.
        boundary_points : list[NamedTuple[int, int, int]]
            BoundaryPoint : NamedTuple[int, int, int]
                latitude : int
                    The latitude of the boundary point.
                longitude : int
                    The longitude of the boundary point.
        altitude_limits : list[int, int]
            altitude_min : int
                The minimum altitude that the drone must fly at all times.
            altitude_max : int
                The maximum altitude that the drone must fly at all times.
    """
    # Initialize namedtuples to store latitude/longitude/altitude data for provided points
    Waypoint = namedtuple("Waypoint", ["latitude", "longitude", "altitude"])
    BoundaryPoint = namedtuple("BoundaryPoint", ["latitude", "longitude"])

    # Load the JSON file as a Python dict to be able to easily access the data
    with open(path, encoding="UTF-8") as data_file:
        json_data: dict[Any, Any] = json.load(data_file)

    # Initialize lists to store waypoints & boundary points
    waypoints: list[NamedTuple] = []
    boundary_points: list[NamedTuple] = []

    # Store the lat/lon/altitude for each point into the Waypoints/BoundaryPoint namedtuple
    # Appends each point into a list to be able to packed into the output
    for waypoint in json_data["waypoints"]:
        latitude: int = waypoint["latitude"]
        longitude: int = waypoint["longitude"]
        altitude: int = waypoint["altitude"]

        full_waypoint: NamedTuple = Waypoint(latitude, longitude, altitude)
        waypoints.append(full_waypoint)

    for boundary_point in json_data["flyzones"]["boundaryPoints"]:
        latitude = boundary_point["latitude"]
        longitude = boundary_point["longitude"]

        full_boundary_point: NamedTuple = BoundaryPoint(latitude, longitude)
        boundary_points.append(full_boundary_point)

    # Grab the altitude limits from the JSON file to be able to be stored into a list
    altitude_min: int = json_data["flyzones"]["altitudeMin"]
    altitude_max: int = json_data["flyzones"]["altitudeMax"]

    # Package all data into the GPSData TypedDict to be exported
    waypoint_data: GPSData = {
        "waypoints": waypoints,
        "boundary_points": boundary_points,
        "altitude_limits": [altitude_min, altitude_max],
    }

    return waypoint_data


# If run on its own, use the default data location
if __name__ == "__main__":
    extract_gps("flight/data/waypoint_data.json")
