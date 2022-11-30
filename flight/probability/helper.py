"""
Summary
-------
Several useful functions repeatedly used in other files
"""

from typing import Dict, List, Tuple
from math import sqrt

TEST_AREA = [
    (38.31722979755967,-76.5570186342245),
    (38.3160801028265,-76.55731984244503),
    (38.31600059675041,-76.5568902018946),
    (38.31546739500083,-76.5537620127769),
    (38.31470980862425,-76.5493636141453),
    (38.31424154692598,-76.5466276164690),
    (38.31369801280048,-76.5434238005822),
    (38.3131406794544,-76.54011767488228),
    (38.31508631356025,-76.5396286507867),
    (38.31615083692682,-76.5449773879351),
    (38.31734210679102,-76.5446085046679),
    (38.31859044679581,-76.5519329158383),
    (38.3164700703248,-76.55255360208943),
    (38.31722979755967,-76.5570186342245)
]

AIR_DROP_AREA = [
    (38.31442311312976, -76.54522971451763),
    (38.31421041772561, -76.54400246436776),
    (38.3144070396263, -76.54394394383165),
    (38.31461622313521, -76.54516993186949),
    (38.31442311312976, -76.54522971451763)
]

def calculate_dist(p_1: Tuple[int, int], p_2: Tuple[int, int]) -> float:
    """
    calculates the Euclidian distance between two points

    Parameters
    ----------
    p_1: Tuple[int, int]
        the first point
    p_2: Tuple[int, int]
        The second point

    Returns
    -------
    distance: float
        The Euclidian distance between these two points
    """
    return sqrt((p_1[0] - p_2[0])**2 + (p_1[1] - p_2[1])**2)

def get_bounds(points: List[Tuple[float, float]]) -> Dict[str, List[float]]:
    """
    returns the vertices of the smallest square that encompasses all
    the given points.

    Parameters
    ----------
    points: List[Tuple[float | float]]
        the collection of points that define the given shape

    Returns
    -------
    bounds: dict[chr, List[float]]
        The bounds of the search area
    """
    x_bounds = [float("inf"), float("-inf")]
    y_bounds = [float("inf"), float("-inf")]

    for i, _ in enumerate(points):
        for dim in ((0, x_bounds), (1, y_bounds)):
            if points[i][dim[0]] < dim[1][0]: #smallest x | y
                dim[1][0] = points[i][dim[0]]

            elif points[i][dim[0]] > dim[1][1]: #biggest x | y
                dim[1][1] = points[i][dim[0]]

    return {'x': x_bounds, 'y': y_bounds}

if __name__ == "__main__":
    x = get_bounds(TEST_AREA)
    print(x['x'][1] - x['x'][0])
