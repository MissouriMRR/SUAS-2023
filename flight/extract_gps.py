"""
Contains the extract_gps() function for extracting data out of
the provided waypoint data JSON file for the SUAS competition.
"""
from typing import Any, List, NamedTuple
import json
import argparse
from typing_extensions import TypedDict


# Initialize namedtuples to store latitude/longitude/altitude data for provided points
class Waypoint(NamedTuple):
    """
    NamedTuple storing the data for a single waypoint.

    Attributes
    ----------
    latitude : float
        The latitude of the waypoint.
    longitude : float
        The longitude of the waypoint.
    altitude : float
        The altitude of the waypoint.
    """

    latitude: float
    longitude: float
    altitude: float



class BoundaryPoint(NamedTuple):
    """
    NamedTuple storing the data for a single boundary point.

    Attributes
    ----------
    latitude : float
        The latitude of the boundary point.
    longitude : float
        The longitude of the boundary point.
    """

    latitude: float
    longitude: float


# Initialize GPSData object for sending all data from the file in a single dict
GPSData = TypedDict(
    "GPSData",
    {
        "waypoints": List[Waypoint],
        "boundary_points": List[BoundaryPoint],
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
    GPSData : TypedDict[
        list[Waypoint[float, float, int]], list[BoundaryPoint[float, float]], list[int, int]
        ]
        The data in the waypoint data file
        waypoints : list[Waypoint[float, float, float]]
            Waypoint : Waypoint[float, float, float]
                latitude : float
                    The latitude of the waypoint.
                longitude : float
                    The longitude of the waypoint.
                altitude : float
                    The altitude of the waypoint.
        boundary_points : list[BoundaryPoint[float, float]]
            BoundaryPoint : BoundaryPoint[float, float]
                latitude : float
                    The latitude of the boundary point.
                longitude : float
                    The longitude of the boundary point.
        altitude_limits : list[int, int]
            altitude_min : int
                The minimum altitude that the drone must fly at all times.
            altitude_max : int
                The maximum altitude that the drone must fly at all times.
    """

    # Load the JSON file as a Python dict to be able to easily access the data
    with open(path, encoding="UTF-8") as data_file:
        json_data: dict[str, Any] = json.load(data_file)

    # Initialize lists to store waypoints & boundary points
    waypoints: list[Waypoint] = []
    boundary_points: list[BoundaryPoint] = []

    # Store the lat/lon/altitude for each point into the Waypoints/BoundaryPoint namedtuple
    # Appends each point into a list to be able to packed into the output
    waypoint: dict[str, float]
    for waypoint in json_data["waypoints"]:
        latitude: float = waypoint["latitude"]
        longitude: float = waypoint["longitude"]
        altitude: float = waypoint["altitude"]

        full_waypoint: Waypoint = Waypoint(latitude, longitude, altitude)
        waypoints.append(full_waypoint)

    boundary_point: dict[str, float]
    for boundary_point in json_data["flyzones"]["boundaryPoints"]:
        latitude = boundary_point["latitude"]
        longitude = boundary_point["longitude"]

        full_boundary_point: BoundaryPoint = BoundaryPoint(latitude, longitude)
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
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    extract_gps(vars(args)["file"])
