"""
Summary
-------
Just a test file
"""

from random import randint
from plotter import plot_prob_map
from seeker import Seeker
from cell_map import CellMap
from segmenter import segment


if __name__ == "__main__":
    test_points = [
        (38.31722979755967, -76.5570186342245),
        (38.3160801028265, -76.55731984244503),
        (38.31600059675041, -76.5568902018946),
        (38.31546739500083, -76.5537620127769),
        (38.31470980862425, -76.5493636141453),
        (38.31424154692598, -76.5466276164690),
        (38.31369801280048, -76.5434238005822),
        (38.3131406794544, -76.54011767488228),
        (38.31508631356025, -76.5396286507867),
        (38.31615083692682, -76.5449773879351),
        (38.31734210679102, -76.5446085046679),
        (38.31859044679581, -76.5519329158383),
        (38.3164700703248, -76.55255360208943),
        (38.31722979755967, -76.5570186342245),
    ]
    area = segment(test_points)
    cell_map = CellMap(area, 30)
    seeker = Seeker((4, 108), 1, 4, cell_map)
    print(cell_map.num_valids)
    for _ in range(2000):
        seeker.move((randint(-1, 1), randint(-1, 0)))
    plot_prob_map(cell_map)
