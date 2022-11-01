"""
Functions for finding the closest point within a boundary to a point outside a boundary
"""

from typing import List, Dict, Tuple
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
import utm
import copy


def latlon_to_utm(coords: Dict[str, float]) -> Dict[str, float]:
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

    utm_coords = utm.from_latlon(coords["latitude"], coords["longitude"])
    coords["utm_x"] = utm_coords[0]
    coords["utm_y"] = utm_coords[1]
    coords["utm_zone_number"] = utm_coords[2]
    coords["utm_zone_letter"] = utm_coords[3]
    return coords


def all_latlon_to_utm(list_of_coords: List[Dict[str, float]]) -> List[Dict[str, float]]:
    """Converts a list of dictionaries with latlon data to add utm data

    Parameters
    ----------
    list_of_coords : List[Dict[str, float]]
        A list of dictionaries that contain lat long data

    Returns
    -------
    List[Dict[str, float]]
        list[dict]: An updated list of dictionaries with added utm data
    """

    for i, _ in enumerate(list_of_coords):
        list_of_coords[i] = latlon_to_utm(list_of_coords[i])
    return list_of_coords


def scale_polygon(my_polygon: Polygon, scale_factor: float) -> Polygon:
    """Scale a shapely polygon by a percentage amount

    Parameters
    ----------
    my_polygon : Polygon
        Polygon that will be scaled
    scale_factor : float, optional
        Amount the polygon will be scaled

    Returns
    -------
    Polygon
        Scale a shapely polygon by a percentage amount
    """

    x_s = list(my_polygon.exterior.coords.xy[0])
    y_s = list(my_polygon.exterior.coords.xy[1])
    x_center = 0.5 * min(x_s) + 0.5 * max(x_s)
    y_center = 0.5 * min(y_s) + 0.5 * max(y_s)
    min_corner = Point(min(x_s), min(y_s))
    center = Point(x_center, y_center)
    shrink_distance = center.distance(min_corner) * scale_factor
    my_polygon_resized = my_polygon.buffer(-shrink_distance)

    return my_polygon_resized


def find_closest_point(
    odlc: Dict[str, float],
    boundary_points: List[Dict[str, float]],
    obstacles: List[Dict[str, float]] = copy.deepcopy([]),
) -> Tuple[Dict[str, float], List[float]]:
    """Finds the closest safe point to the ODLC while staying within the flight boundary

    Parameters
    ----------
    odlc : Dict[str, float]
        Point data for the ODLC object
    boundary_points : List[Dict[str, float]]
        Point data which makes up the flight boundary

    Other Parameters
    ----------------
    obstacles : List[Dict[str, float]]
        Point data for the obstacles

    Returns
    -------
    Tuple[Dict[str, float], List[float]]
        Closest safe point, and the shrunken boundary (for plotting)
    """

    poly_points = [(point["utm_x"], point["utm_y"]) for point in boundary_points]

    boundary_shape = Polygon(poly_points)
    odlc_shape = Point(odlc["utm_x"], odlc["utm_y"])

    for obstacle in obstacles:
        # create obstacle as shapely shape
        circle = (
            Point(obstacle["utm_x"], obstacle["utm_y"])
            .buffer(obstacle["radius"])
            .boundary
        )
        obstacle_shape = Polygon(circle)

        # remove obstacle area from boundary polygon
        boundary_shape = boundary_shape.difference(obstacle_shape)

    # scale down boundary by 1% to add a safety margin
    boundary_shape = scale_polygon(boundary_shape, 0.01)

    p_1, _ = nearest_points(
        boundary_shape, odlc_shape
    )  # point returned in same order as input shapes

    closest_point = p_1

    zone_number = odlc["utm_zone_number"]
    zone_letter = odlc["utm_zone_letter"]

    return (
        {
            "utm_x": closest_point.x,
            "utm_y": closest_point.y,
            "utm_zone_number": zone_number,
            "utm_zone_letter": zone_letter,
            "latitude": utm.to_latlon(
                closest_point.x, closest_point.y, zone_number, zone_letter
            )[0],
            "longitude": utm.to_latlon(
                closest_point.x, closest_point.y, zone_number, zone_letter
            )[1],
        },
        list(
            zip(*boundary_shape.exterior.coords.xy)
        ),  # pylint: disable=maybe-no-member
    )
