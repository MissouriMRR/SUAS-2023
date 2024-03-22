"""
Contains the extract_gps() function for extracting data out of
the provided waypoint data JSON file for the SUAS competition.
"""

import argparse
import json
from typing import Any, NamedTuple
from typing_extensions import TypedDict

import utm


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
        The altitude of the waypoint, in meters
    """

    latitude: float
    longitude: float
    altitude: float


class WaypointUtm(NamedTuple):
    """
    NamedTuple storing the data for a single waypoint using UTM coordinates.

    Attributes
    ----------
    easting : float
        The easting of the waypoint.
    northing : float
        The northing of the waypoint.
    zone_number : int
        The zone number of the waypoint.
    zone_letter : str
        The zone letter of the waypoint.
    altitude : float
        The altitude of the waypoint.
    """

    easting: float
    northing: float
    zone_number: int
    zone_letter: str
    altitude: float


class OdlcWaypoint(NamedTuple):
    """
    NamedTuple storing the data for a single ODLC waypoint.

    Attributes
    ----------
    latitude : float
        The latitude of the waypoint.
    longitude : float
        The longitude of the waypoint.
    """

    latitude: float
    longitude: float


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


class BoundaryPointUtm(NamedTuple):
    """
    NamedTuple storing the data for a single boundary point using UTM coordinates.

    Attributes
    ----------
    easting : float
        The easting of the boundary point.
    northing : float
        The northing of the boundary point.
    zone_number : int
        The zone number of the boundary point.
    zone_letter : str
        The zone letter of the boundary point.
    """

    easting: float
    northing: float
    zone_number: int
    zone_letter: str


# Initialize GPSData object for sending all data from the file in a single dict
GPSData = TypedDict(
    "GPSData",
    {
        "waypoints": list[Waypoint],
        "waypoints_utm": list[WaypointUtm],
        "odlc_waypoints": list[OdlcWaypoint],
        "boundary_points": list[BoundaryPoint],
        "boundary_points_utm": list[BoundaryPointUtm],
        "altitude_limits": list[int],
        "odlc_altitude": int,
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
            list[Waypoint[float, float, float]],
            list[WaypointUtm[float, float, int, str, float]],
            list[OdlcWaypoint[float, float]],
            list[BoundaryPoint[float, float]],
            list[BoundaryPointUtm[float, float, int, str]],
            list[int, int, int],
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
        waypoints_utm : list[WaypointUtm[float, float, int, str, float]]
            WaypointUtm : WaypointUtm[float, float, int, str, float]
                easting : float
                    The easting of the waypoint.
                northing : float
                    The northing of the waypoint.
                zone_number : int
                    The zone number of the waypoint.
                zone_letter : str
                    The zone letter of the waypoint.
                altitude : float
                    The altitude of the waypoint.
        odlc_waypoints : list[OdlcWaypoint[float, float]]
            OdlcWaypoint : OdlcWaypoint[float, float]
                latitude : float
                    The latitude of the waypoint.
                longitude : float
                    The longitude of the waypoint.
        boundary_points : list[BoundaryPoint[float, float]]
            BoundaryPoint : BoundaryPoint[float, float]
                latitude : float
                    The latitude of the boundary point.
                longitude : float
                    The longitude of the boundary point.
        boundary_points_utm : list[BoundaryPointUtm[float, float, int, str]]
            BoundaryPointUtm : BoundaryPointUtm[float, float, int, str]
                easting : float
                    The easting of the boundary point.
                northing : float
                    The northing of the boundary point.
                zone_number : int
                    The zone number of the boundary point.
                zone_letter : str
                    The zone letter of the boundary point.
        altitude_limits : list[int, int]
            altitude_min : int
                The minimum altitude that the drone must fly at all times, in feet.
            altitude_max : int
                The maximum altitude that the drone must fly at all times, in feet.
        odlc_altitude : int
            The altitude to fly at during the ODLC state, in feet.
    """

    # Load the JSON file as a Python dict to be able to easily access the data
    with open(path, encoding="UTF-8") as data_file:
        json_data: dict[str, Any] = json.load(data_file)

    # Initialize lists to store waypoints & boundary points
    waypoints: list[Waypoint] = []
    waypoints_utm: list[WaypointUtm] = []
    odlc_waypoints: list[OdlcWaypoint] = []
    boundary_points: list[BoundaryPoint] = []
    boundary_points_utm: list[BoundaryPointUtm] = []

    # Get forced UTM zone number and zone letter
    forced_zone_number: int
    forced_zone_letter: str
    _, _, forced_zone_number, forced_zone_letter = utm.from_latlon(
        json_data["flyzones"]["boundaryPoints"][0]["latitude"],
        json_data["flyzones"]["boundaryPoints"][0]["longitude"],
    )

    # Store the lat/lon/altitude for each point into the Waypoints/BoundaryPoint namedtuple
    # Appends each point into a list to be able to packed into the output
    waypoint: dict[str, float]
    for waypoint in json_data["waypoints"]:
        latitude: float = waypoint["latitude"]
        longitude: float = waypoint["longitude"]
        altitude: float = waypoint["altitude"]

        waypoints.append(Waypoint(latitude, longitude, altitude))
        utm_coords: tuple[float, float, int, str] = utm.from_latlon(
            latitude, longitude, forced_zone_number, forced_zone_letter
        )
        full_waypoint_utm: WaypointUtm = WaypointUtm(*utm_coords, altitude)
        waypoints_utm.append(full_waypoint_utm)

    odlc_waypoint: dict[str, float]
    for odlc_waypoint in json_data["odlcWaypoints"]:
        latitude = odlc_waypoint["latitude"]
        longitude = odlc_waypoint["longitude"]
        odlc_waypoints.append(OdlcWaypoint(latitude, longitude))

    boundary_point: dict[str, float]
    for boundary_point in json_data["flyzones"]["boundaryPoints"]:
        latitude = boundary_point["latitude"]
        longitude = boundary_point["longitude"]

        boundary_points.append(BoundaryPoint(latitude, longitude))
        full_boundary_point_utm: BoundaryPointUtm = BoundaryPointUtm(
            *utm.from_latlon(latitude, longitude, forced_zone_number, forced_zone_letter)
        )
        boundary_points_utm.append(full_boundary_point_utm)

    # Package all data into the GPSData TypedDict to be exported
    waypoint_data: GPSData = {
        "waypoints": waypoints,
        "waypoints_utm": waypoints_utm,
        "odlc_waypoints": odlc_waypoints,
        "boundary_points": boundary_points,
        "boundary_points_utm": boundary_points_utm,
        "altitude_limits": [
            json_data["flyzones"]["altitudeMin"],
            json_data["flyzones"]["altitudeMax"],
        ],
        "odlc_altitude": json_data["odlcAltitude"],
    }
    return waypoint_data


# If run on its own, use the default data location
if __name__ == "__main__":
    # Read file to be used as the data file using the -file argument
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-file")
    args: argparse.Namespace = parser.parse_args()

    extract_gps(vars(args)["file"])
