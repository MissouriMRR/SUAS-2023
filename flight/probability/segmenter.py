from typing import Iterable, List, Tuple
from helper import get_bounds
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import math
"""
Divides the ODLC search area into identical cells.
"""

CELL_SIZE = 0.00015
CENTER_OFFSET = CELL_SIZE / 2

def segment(polygon: List[Tuple[float, float]]) -> List[List[Tuple[float, float] | str]]:
    """
    divides the ODLC search area into a probability map

    Parameters
    ----------
    polygon: List[Tuple[int, int]]
        A list of points defining the polygon
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
            p = Point(x_val, y_val)
            if within_check.contains(p):
                row.append((x_val, y_val))
            else:
                row.append('X')
        prob_map_points.append(row)
    
    return prob_map_points

if __name__ == "__main__":
    pass


    

