"""
Provides plotting functionality for visaulizing coordinate data
"""

from typing import List, Dict, Tuple
from cell_map import CellMap
from segmenter import segment
from helper import get_bounds
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import copy

P_1_COLOR = (246, 229, 37)
P_0_COLOR = (38, 7, 144)


def get_p_color(p: float) -> List[float]:
    """
    Given a probability [0, 1], return the color
    of the cell.

    Parameters
    ----------
    p : float
        the probability of a ODLC being found in the cell
    """
    color = []
    for i in range(3):
        color.append((P_0_COLOR[i] + ((P_1_COLOR[i] - P_0_COLOR[i]) * p)) / 255)
    return color


def draw_cell(x: float | None, y: float | None, p: float) -> None:
    """
    draws a cell on the plot

    Parameters
    ----------
    x : float | None
        the x-coordinate of the cell. Cancels the function call if none
    y : float | None
        the y-coordinate of the cell. Cancels the function call if none
    p : float
        The probability of the cell containing a ODLC
    """
    if x == None or y == None: return
    plt.gca().add_patch(
        patches.Rectangle((x, y), 0.00015, 0.00015, fill=True, color=get_p_color(p))
    )


def get_normalized_prob(prob_map: CellMap) -> List[float]:
    low, high = float("inf"), float("-inf")
    for i in range(len(prob_map.data)):
        for j in range(len(prob_map[0])):
            prob = prob_map[i][j].probability
            if prob > high:
                high = prob
            elif prob < low:
                low = prob
    return [low, high]


def plot_prob_map(prob_map: CellMap, seen_mode: bool = False) -> None:
    """
    creates a visual of the current probability map.

    Parameters
    ----------
    prob_map: object
        the position of each cell and its probability of containing a
        drop point.
    """
    prob_range = get_normalized_prob(prob_map)
    MARGIN = 0.001
    size = max(
        abs(prob_map.bounds["x"][0] - prob_map.bounds["x"][1]),
        abs(prob_map.bounds["y"][0] - prob_map.bounds["y"][1]),
    )
    plt.xlim(prob_map.bounds["x"][0] - MARGIN, prob_map.bounds["x"][0] + size + MARGIN)
    plt.ylim(prob_map.bounds["y"][0] - MARGIN, prob_map.bounds["y"][0] + size + MARGIN)

    for i in range(len(prob_map.data)):
        for j in range(len(prob_map[0])):
            cell = prob_map[i][j]
            if cell.is_valid:
                if seen_mode:
                    draw_cell(cell.x, cell.y, 1 if cell.seen else 0)
                else:
                    draw_cell(
                        cell.x,
                        cell.y,
                        (cell.probability - prob_range[0])
                        / (prob_range[1] - prob_range[0]),
                    )
    plt.show()


def plot_data(
    odlc: Dict[str, float],
    closest_point: Dict[str, float],
    old_boundary: List[Dict[str, float]],
    new_boundary: List[Tuple[float, float]],
    obstacles: List[Dict[str, float]] = copy.deepcopy([]),
) -> None:
    """Plots the waypoints, obstacles, and flight path between waypoints

    Parameters
    ----------
    odlc : Dict[str, float]
        Point data for ODLC point
    closest_point : Dict[str, float]
        Point data for closest point to ODLC point
    old_boundary : List[Dict[str, float]]
        Point data for flight boundary
    new_boundary : List[Tuple[float, float]]
        Point data for shrunked flight boundary

    Other Parameters
    ----------------
    obstacles: List[Dict[str, float]]
        Point data for all obstacles
    """

    # plot obstacles
    for obstacle in obstacles:
        x = obstacle["utm_x"]
        y = obstacle["utm_y"]
        radius = obstacle["radius"]

        plt.gca().add_patch(plt.Circle((x, y), radius, color="red"))

    # plot boundary 1
    x_1, y_1 = [], []
    for point in old_boundary:
        x_1.append(point["utm_x"])
        y_1.append(point["utm_y"])
    plt.plot(x_1, y_1, "ro-")

    # plot boundary 2
    x_2, y_2 = [], []
    for point2 in new_boundary:
        x_2.append(point2[0])
        y_2.append(point2[1])
    plt.plot(x_2, y_2, "bo-")

    # plot odlc and closest point to odlc
    plt.plot(odlc["utm_x"], odlc["utm_y"], marker="*")
    plt.plot(closest_point["utm_x"], closest_point["utm_y"], marker="*")

    plt.gca().set_aspect(1)
    plt.show()


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
    plot_prob_map(CellMap(segment(test_points)))
