"""
Provides plotting functionality for visualizing coordinate data
"""

from typing import List, Dict, Tuple
import matplotlib.pyplot as plt


def plot_data(
    odlc: Dict[str, float],
    closest_point: Dict[str, float],
    old_boundary: List[Dict[str, float]],
    new_boundary: List[Tuple[float, float]],
    obstacles: List[Dict[str, float]],
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
    obstacles : List[Dict[str, float]]
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