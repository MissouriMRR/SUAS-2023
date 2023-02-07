"""
Several useful functions repeatedly used in other files
"""

# pylint: disable=C0200
#NOTE: removes "consider using enumerate" error

from math import sqrt

AIR_DROP_AREA: list[tuple[float, float]] = [
    (38.31442311312976, -76.54522971451763),
    (38.31421041772561, -76.54400246436776),
    (38.3144070396263, -76.54394394383165),
    (38.31461622313521, -76.54516993186949),
    (38.31442311312976, -76.54522971451763),
]


def calculate_dist(p_1: tuple[float, float], p_2: tuple[float, float]) -> float:
    """
    calculates the Euclidian distance between two points

    Parameters
    ----------
    p_1: tuple[float, float]
        the first point
    p_2: tuple[float, float]
        The second point

    Returns
    -------
    distance: float
        The Euclidian distance between these two points
    """
    return sqrt((p_1[0] - p_2[0]) ** 2 + (p_1[1] - p_2[1]) ** 2)


def get_bounds(points: list[tuple[float, float]]) -> dict[str, list[float]]:
    """
    returns the vertices of the smallest square that encompasses all
    the given points.

    Parameters
    ----------
    points: list[tuple[float | float]]
        the collection of points that define the given shape

    Returns
    -------
    bounds: dict[str, list[float]]
        The bounds of the search area
    """
    x_bounds: list[float] = [float("inf"), float("-inf")]
    y_bounds: list[float] = [float("inf"), float("-inf")]

    i: int
    for i in range(len(points)):
        dim: tuple[int, list[float]]
        for dim in ((0, x_bounds), (1, y_bounds)):
            if points[i][dim[0]] < dim[1][0]:  # smallest x | y
                dim[1][0] = points[i][dim[0]]

            elif points[i][dim[0]] > dim[1][1]:  # biggest x | y
                dim[1][1] = points[i][dim[0]]

    return {"x": x_bounds, "y": y_bounds}
