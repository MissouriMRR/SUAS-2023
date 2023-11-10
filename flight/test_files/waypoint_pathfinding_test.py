"""Run tests for waypoint pathfinding."""

import json
from pathlib import Path
from typing import TypedDict

import utm

from flight.waypoint.geometry import Point
from flight.waypoint.graph import GraphNode
from flight.waypoint import pathfinding


class Coordinate(TypedDict):
    """A coordinate in waypoint_data.json"""

    latitude: float
    longitude: float


class Flyzones(TypedDict):
    """flyzones in waypoint_data.json"""

    altitudeMin: float
    altitudeMax: float
    boundaryPoints: list[Coordinate]


class WaypointData(TypedDict):
    """TypedDict representing waypoint_data.json"""

    flyzones: Flyzones
    waypoints: list[Coordinate]


def draw_graph(nodes: list[GraphNode[Point, float]]) -> str:
    """
    Generate an SVG drawing of a graph.

    Parameters
    ----------
    nodes : list[GraphNode[Point, float]]
        The nodes in the graph.

    Returns
    -------
    str
        The SVG code representing the drawing of the graph.
    """
    svg_size: int = 1000

    string_builder: list[str] = []
    string_builder.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{svg_size}" height="{svg_size}"'
        f' viewBox="0 0 {svg_size} {svg_size}">'
    )

    xmin: float = min(node.value.x for node in nodes)
    xmax: float = max(node.value.x for node in nodes)
    ymin: float = min(node.value.y for node in nodes)
    ymax: float = max(node.value.y for node in nodes)

    size: float = max(xmax - xmin, ymax - ymin)

    center_x: float = (xmin + xmax) / 2
    center_y: float = (ymin + ymax) / 2
    xmin = center_x - 0.6 * size
    xmax = center_x + 0.6 * size
    ymin = center_y - 0.6 * size
    ymax = center_y + 0.6 * size

    def svg_coord(x: float, y: float) -> tuple[float, float]:
        t_x: float = (x - xmin) / (xmax - xmin)
        t_y: float = (y - ymin) / (ymax - ymin)
        return t_x * svg_size, (1 - t_y) * svg_size

    for node_1 in nodes:
        for node_2 in nodes:
            if node_1 == node_2:
                continue

            if not node_1.is_connected_to(node_2):
                continue

            x_1, y_1 = svg_coord(node_1.value.x, node_1.value.y)
            x_2, y_2 = svg_coord(node_2.value.x, node_2.value.y)

            string_builder.append(
                f'<path d="M {x_1},{y_1} L {x_2},{y_2}" stroke-width="1" stroke="black"/>'
            )

    for node in nodes:
        x, y = svg_coord(node.value.x, node.value.y)
        string_builder.append(f'<circle cx="{x}" cy="{y}" r="4" fill="black"/>')

    string_builder.append("</svg>")

    return "".join(string_builder)


def main() -> None:
    """Run tests for waypoint pathfinding."""
    waypoint_data_filepath: str = str(
        Path(__file__)
        .parent.absolute()
        .joinpath("..")
        .joinpath("data")
        .joinpath("waypoint_data.json")
    )
    with open(waypoint_data_filepath, "r", encoding="utf-8") as file:
        waypoint_data: WaypointData = json.load(file)

    boundary_coords: list[Coordinate] = waypoint_data["flyzones"]["boundaryPoints"]
    boundary_coords.pop()  # The last point is a duplicate of the first in the json
    force_zone_number: int
    force_zone_letter: str
    _, _, force_zone_number, force_zone_letter = utm.from_latlon(
        boundary_coords[0]["latitude"], boundary_coords[0]["longitude"]
    )

    boundary_vertices: list[Point] = []
    for coord in waypoint_data["flyzones"]["boundaryPoints"]:
        easting, northing, _, _ = utm.from_latlon(
            coord["latitude"], coord["longitude"], force_zone_number, force_zone_letter
        )
        boundary_vertices.append(Point(easting, northing))

    graph: list[GraphNode[Point, float]] = pathfinding.create_pathfinding_graph(
        boundary_vertices, 0.0
    )
    print(draw_graph(graph))


if __name__ == "__main__":
    main()
