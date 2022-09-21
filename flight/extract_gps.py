"""Contains the extract_gps() function for extracting data out of
the provided waypoint data JSON file for the SUAS competition."""
from collections import namedtuple
from typing import NamedTuple
import json
from typing_extensions import TypedDict

GPSData = TypedDict(
    "GPSData",
    {
        "waypoints": list(NamedTuple(int, int, int)),
        "boundary_points": list(NamedTuple(int, int)),
        "altitude_limits": list(int, int),
    },
)


def extract_gps(path: str) -> GPSData:
    """Returns the waypoints, boundary points, and altitude limits from a waypoint data file.

    Args:
        path (str): File path to the waypoint data JSON file.

    Returns:
        GPSData: TypedDict[
            list(NamedTuple(int, int, int)), list(NamedTuple(int, int)), list(int, int)
        ]
            The data in the waypoint data file
            waypoints : list(NamedTuple(int, int, int))
                Waypoint : NamedTuple(int, int, int)
                    latitude : int
                        The latitude of the waypoint.
                    longitude : int
                        The longitude of the waypoint.
                    altitude : int
                        The altitude of the waypoint.
            boundary_points : list(NamedTuple(int, int, int))
                BoundaryPoint : NamedTuple(int, int, int)
                    latitude : int
                        The latitude of the boundary point.
                    longitude : int
                        The longitude of the boundary point.
            altitude_limits : list(int, int)
                altitude_min : int
                    The minimum altitude that the drone must fly at all times.
                altitude_max : int
                    The maximum altitude that the drone must fly at all times.
    """

    Waypoint = namedtuple("Waypoint", ["latitude", "longitude", "altitude"])
    BoundaryPoint = namedtuple("BoundaryPoint", ["latitude", "longitude"])

    with open(path, encoding="UTF-8") as data_file:
        json_data = json.load(data_file)

    waypoints = []
    boundary_points = []

    for waypoint in json_data["waypoints"]:
        latitude = waypoint["latitude"]
        longitude = waypoint["longitude"]
        altitude = waypoint["altitude"]

        waypoint = Waypoint(latitude, longitude, altitude)
        waypoints.append(waypoint)

    print("Boundary Points Loaded:")
    for boundary_point in json_data["flyzones"]["boundaryPoints"]:
        latitude = boundary_point["latitude"]
        longitude = boundary_point["longitude"]

        boundary_point = BoundaryPoint(latitude, longitude)
        boundary_points.append(boundary_point)

    altitude_min = json_data["flyzones"]["altitudeMin"]
    altitude_max = json_data["flyzones"]["altitudeMax"]

    waypoint_data: GPSData = {
        "waypoints": waypoints,
        "boundary_points": boundary_points,
        "altitude_limits": [altitude_min, altitude_max],
    }

    return waypoint_data


if __name__ == "__main__":
    extract_gps("flight/waypoint_data.json")
