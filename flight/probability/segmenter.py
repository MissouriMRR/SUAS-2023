"""
Summary
-------
Defines the public 'segment' function that allows a polygon to be divided
into uniform squares
"""
from math import ceil, sin, cos, asin
from typing import List, Tuple
from helper import get_bounds, AIR_DROP_AREA, calculate_dist
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

CELL_SIZE = 0.00015
c = calculate_dist(AIR_DROP_AREA[0], AIR_DROP_AREA[1])
b = AIR_DROP_AREA[1][0] - AIR_DROP_AREA[0][0]
SUAS_2023_THETA = asin(b / c)


def segment(
    polygon: List[Tuple[float, float]], cell_size: float = CELL_SIZE, rotate: float = 0
) -> List[List[Tuple[float, float] | str]]:
    """
    divides the ODLC search area into a probability map

    Parameters
    ----------
    polygon: List[Tuple[float, float]]
        A list of points defining the polygon
    cell_size : float
        The size (in degrees of latitude) of each segment

    Returns
    -------
    segmented_area : List[List[Tuple[float, float], | str]]
        The new area divided into equally sized squares, with some
        squares simply being 'X' to represent that they are out of
        bounds
    """
    CENTER_OFFSET = cell_size / 2
    prob_map_points = []
    bounds = get_bounds(polygon)
    within_check = Polygon(polygon)
    for i in range(ceil((bounds["x"][1] - bounds["x"][0]) / cell_size)):
        row: List[Tuple[float, float] | str] = []
        for j in range(ceil((bounds["y"][1] - bounds["y"][0]) / cell_size)):
            # check if point is within polygon
            x_val = bounds["x"][0] + CENTER_OFFSET + (i * cell_size)
            y_val = bounds["y"][0] + CENTER_OFFSET + (j * cell_size)
            geo_point = Point(x_val, y_val)
            if within_check.contains(geo_point):
                new_point = rotate_point((x_val, y_val), -SUAS_2023_THETA, AIR_DROP_AREA[0])
                row.append((new_point[0], new_point[1]))
            else:
                row.append("X")
        prob_map_points.append(row)

    return prob_map_points


def rotate_point(
    point: Tuple[float, float], theta: float, p_of_r: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Rotates a given x,y point theta degrees around any arbitrary point.

    Parameters
    ----------
    point: Tuple[float, float]
        the point to be rotated
    theta: float
        the angle to be rotated by
    p_of_r: Tuple[float, float]
        the point of rotation

    Returns
    -------
    rotated_point : Tuple[float, float]
        the coordinates of the rotated point
    """
    x0, xc = point[0], p_of_r[0]
    y0, yc = point[1], p_of_r[1]
    return (
        ((x0 - xc) * cos(theta) - (y0 - yc) * sin(theta) + xc),
        ((x0 - xc) * sin(theta) + (y0 - yc) * cos(theta) + yc),
    )


def rotate_shape(
    shape: List[Tuple[float, float]], theta: float, p_of_r: Tuple[float, float]
) -> List[Tuple[float, float]]:
    """
    Rotates an entire collection of points

    Parameters
    ----------
    shape: List[Tuple[float, float]]
        the collection of points
    theta : float
        the angle to rotate by
    p_of_r : Tuple[int, int]
        point of rotation
    """
    new_shape = []
    for point in shape:
        new_shape.append(rotate_point(point, theta, p_of_r))
    return new_shape


if __name__ == "__main__":
    pass
