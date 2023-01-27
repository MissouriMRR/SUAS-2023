"""
Provides plotting functionality for visaulizing coordinate data
"""

from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib import patches
from flight.search.cell_map import CellMap
from flight.search.cell import Cell
from flight.search.segmenter import segment, SUAS_2023_THETA, rotate_shape
from flight.search.helper import AIR_DROP_AREA
from flight.search.plot_algo import get_plot

# the color used when drawing the search area's cells
CELL_COLOR: tuple[float, float, float] = (246 / 256, 229 / 256, 37 / 256)


def draw_cell(pos: tuple[float | None, float | None]) -> None:
    """
    draws a cell on the plot

    Parameters
    ----------
    pos : tuple(float, float) | None
        the position of the cell
    """
    plt.gca().add_patch(
        patches.Rectangle(
            (pos[0], pos[1]), 0.00015, 0.00015, fill=True, color=CELL_COLOR
        )
    )


def plot_path(
    prob_map: CellMap, path: list[tuple[float, float]] = deepcopy([])
) -> None:
    """
    creates a visual of the current probability map.

    Parameters
    ----------
    prob_map: CellMap
        the position of each cell and its probability of containing a
        drop point.
    path : list[tuple[float, float]]
        The latitude longitude coordinates of every point the drone visits
    """
    margin: float = 0.001
    size: float = max(
        abs(prob_map.bounds["x"][0] - prob_map.bounds["x"][1]),
        abs(prob_map.bounds["y"][0] - prob_map.bounds["y"][1]),
    )
    plt.xlim(prob_map.bounds["x"][0] - margin, prob_map.bounds["x"][0] + size + margin)
    plt.ylim(prob_map.bounds["y"][0] - margin, prob_map.bounds["y"][0] + size + margin)

    i: int
    j: int
    for i in range(len(prob_map.data)):
        for j in range(len(prob_map[0])):
            cell: Cell = prob_map[i][j]
            if cell.is_valid:
                draw_cell((cell.lat, cell.lon))

    x: list[float] = []  # pylint: disable=C0103
    y: list[float] = []  # pylint: disable=C0103
    for point in path:
        x.append(point[0])
        y.append(point[1])
    plt.plot(x, y, "-")

    plt.show()


if __name__ == "__main__":
    plot_path(
        CellMap(
            segment(
                rotate_shape(AIR_DROP_AREA, SUAS_2023_THETA, AIR_DROP_AREA[0]),
                0.000025,
                SUAS_2023_THETA,
                AIR_DROP_AREA[0],
            )
        ),
        get_plot(),
    )
