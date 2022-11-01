"""
Summary
-------
Defines the public 'segment' function that allows a polygon to be divided
into uniform squares
"""
import math
from typing import List, Tuple
from helper import get_bounds
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

CELL_SIZE = 0.00015
CENTER_OFFSET = CELL_SIZE / 2

def segment(polygon: List[Tuple[float, float]]) -> List[List[Tuple[float, float] | str]]:
    """
    divides the ODLC search area into a probability map

    Parameters
    ----------
    polygon: List[Tuple[float, float]]
        A list of points defining the polygon

    Returns
    -------
    segmented_area : List[List[Tuple[float, float], | str]]
        The new area divided into equally sized squares, with some
        squares simply being 'X' to represent that they are out of
        bounds
    """
    prob_map_points = []
    bounds = get_bounds(polygon)
    within_check = Polygon(polygon)
    for i in range(math.ceil((bounds['x'][1] - bounds['x'][0]) / CELL_SIZE)):
        row: List[Tuple[float, float] | str] = []
        for j in range(math.ceil((bounds['y'][1] - bounds['y'][0]) / CELL_SIZE)):
            #check if point is within polygon
            x_val = bounds['x'][0] + CENTER_OFFSET + (i * CELL_SIZE)
            y_val = bounds['y'][0] + CENTER_OFFSET + (j * CELL_SIZE)
            geo_point = Point(x_val, y_val)
            if within_check.contains(geo_point):
                row.append((x_val, y_val))
            else:
                row.append('X')
        prob_map_points.append(row)

    return prob_map_points

if __name__ == "__main__":
    pass
