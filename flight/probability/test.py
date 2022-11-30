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
from helper import AIR_DROP_AREA


if __name__ == "__main__":
    area = segment(AIR_DROP_AREA, 0.000025)
    cell_map = CellMap(area, 30)
    seeker = Seeker((4, 108), 1, 4, cell_map)
    print(cell_map.num_valids)
    for _ in range(2000):
        seeker.move((randint(-1, 1), randint(-1, 0)))
    plot_prob_map(cell_map)
