"""
Defines the public 'segment' function that allows a polygon to be divided
into uniform squares
"""

from math import ceil, sin, cos, asin
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from flight.search.helper import get_bounds, AIR_DROP_AREA, calculate_dist

CELL_SIZE: float = 0.00015
c: float = calculate_dist(AIR_DROP_AREA[0], AIR_DROP_AREA[1])  # the hypotenuse
b: float = AIR_DROP_AREA[1][0] - AIR_DROP_AREA[0][0]  # another side length
SUAS_2023_THETA: float = asin(b / c)  # the angle to rotate the SUAS_2023 area


def segment(
    polygon: list[tuple[float, float]],
    cell_size: float = CELL_SIZE,
    rotated: float = 0,
    p_of_r: tuple[float, float] = (-1.0, -1.0),
) -> list[list[tuple[float, float] | str]]:
    """
    divides the ODLC search area into a probability map

    Parameters
    ----------
    polygon: list[tuple[float, float]]
        A list of points defining the polygon
    cell_size : float
        The size (in degrees of latitude) of each segment
    rotated: float
        the radians the shape has been rotated
    p_of_r: tuple[float, float]
        the point the shape was rotated about

    Returns
    -------
    segmented_area : list[list[tuple[float, float], | str]]
        The new area divided into equally sized squares, with some
        squares simply being 'X' to represent that they are out of
        bounds
    """
    center_offset: float = cell_size / 2
    prob_map_points: list[list[tuple[float, float] | str]] = []
    bounds: dict[str, list[float]] = get_bounds(polygon)
    within_check: Polygon = Polygon(polygon)
    i: int
    j: int
    for i in range(ceil((bounds["x"][1] - bounds["x"][0]) / cell_size)):
        row: list[tuple[float, float] | str] = []
        for j in range(ceil((bounds["y"][1] - bounds["y"][0]) / cell_size)):
            # check if point is within polygon
            x_val: float = bounds["x"][0] + center_offset + (i * cell_size)
            y_val: float = bounds["y"][0] + center_offset + (j * cell_size)
            geo_point: Point = Point(x_val, y_val)
            if within_check.contains(geo_point):
                new_point = rotate_point((x_val, y_val), -rotated, p_of_r)
                row.append((new_point[0], new_point[1]))
            else:
                row.append("X")
        prob_map_points.append(row)

    return prob_map_points


def rotate_point(
    point: tuple[float, float], theta: float, p_of_r: tuple[float, float]
) -> tuple[float, float]:
    """
    Rotates a given x,y point theta degrees around any arbitrary point.

    Parameters
    ----------
    point: tuple[float, float]
        the point to be rotated
    theta: float
        the angle to be rotated by
    p_of_r: tuple[float, float]
        the point of rotation

    Returns
    -------
    rotated_point : tuple[float, float]
        the coordinates of the rotated point
    """
    x_init: float = point[0]
    x_rot: float = p_of_r[0]
    y_init: float = point[1]
    y_rot: float = p_of_r[1]
    return (
        ((x_init - x_rot) * cos(theta) - (y_init - y_rot) * sin(theta) + x_rot),
        ((x_init - x_rot) * sin(theta) + (y_init - y_rot) * cos(theta) + y_rot),
    )


def rotate_shape(
    shape: list[tuple[float, float]], theta: float, p_of_r: tuple[float, float]
) -> list[tuple[float, float]]:
    """
    Rotates an entire collection of points

    Parameters
    ----------
    shape: list[tuple[float, float]]
        the collection of points
    theta : float
        the angle to rotate by
    p_of_r : tuple[float, float]
        point of rotation

    Returns
    -------
    rotated_shape: list[tuple[float, float]]
        the coordinates of the rotated shape
    """
    new_shape: list[tuple[float, float]] = []
    point: tuple[float, float]
    for point in shape:
        new_shape.append(rotate_point(point, theta, p_of_r))
    return new_shape


if __name__ == "__main__":
    pass
