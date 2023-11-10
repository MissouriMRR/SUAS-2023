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
    svg_xmin: int = 0
    svg_xmax: int = 512
    svg_ymin: int = 0
    svg_ymax: int = 512

    string_builder: list[str] = []
    string_builder.append(
        f'<svg xmlns="http://www.w3.org/2000/svg"'
        f' width="{svg_xmax - svg_ymin}" height="{svg_ymax - svg_ymin}"'
        f' viewBox="{svg_xmin} {svg_ymin} {svg_xmax} {svg_ymax}">'
    )

    xmin: float = min(node.value.x for node in nodes)
    xmax: float = max(node.value.x for node in nodes)
    ymin: float = min(node.value.y for node in nodes)
    ymax: float = max(node.value.y for node in nodes)

    width: float = xmax - xmin
    height: float = ymax - ymin

    xmin -= 0.2 * width
    xmax += 0.2 * width
    ymin -= 0.2 * height
    ymax += 0.2 * height

    def svg_coord(x: float, y: float) -> tuple[float, float]:
        t_x: float = (x - xmin) / (xmax - xmin)
        t_y: float = (y - ymin) / (ymax - ymin)
        return (1 - t_x) * svg_xmin + t_x * svg_xmax, (1 - t_y) * svg_ymax + t_y * svg_ymin

    for node in nodes:
        point: Point = node.value
        x, y = svg_coord(point.x, point.y)
        string_builder.append(f'<circle cx="{x}" cy="{y}" r="5" fill="black"/>')

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
