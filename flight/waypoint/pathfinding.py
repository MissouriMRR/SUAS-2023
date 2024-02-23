"""
Defines a function to find the shortest path between two waypoints that
stays within the mission flight boundary.
"""

import heapq
from typing import Iterable, NamedTuple, TypeAlias

from flight.waypoint.geometry import LineSegment, Point
from flight.waypoint.graph import GraphNode

Node: TypeAlias = GraphNode[Point, float]


class _SearchNode(NamedTuple):
    """
    Contains a node to visit. Used when searching a graph.

    Attributes
    ----------
    priority : float
        The priority of the node to search. A lower value means a higher
        priority.
    distance_so_far : float
        The distance traveled to get to this node.
    visitor : Node
        The node that is visiting.
    node : Node
        The node to visit.
    """

    priority: float
    distance_so_far: float
    visitor: Node | None
    node: Node


def _shrink_line_segment(line_segment: LineSegment) -> LineSegment:
    """
    Shrink a line segment slightly. To be used to prevent two line segments
    sharing an endpoint from being considered as intersecting.

    Parameters
    ----------
    line_segment : LineSegment
        The line segment to shrink.

    Returns
    -------
    LineSegment
        A new line segment with the endpoints moved inward very slightly.
    """
    direction: Point = line_segment.p_2 - line_segment.p_1
    direction /= direction.distance_from_origin()
    return LineSegment(line_segment.p_1 + 1e-3 * direction, line_segment.p_2 - 1e-3 * direction)


def _visitors(start_node: Node, goal_node: Node) -> Iterable[Point]:
    """
    Yield the positions of the visitors in a path to a goal node, with the
    goal node being last.

    Parameters
    ----------
    start_node : Node
        The start node in a search.
    goal_node : Node
        The goal node in a search.

    Yields
    -------
    Point
        The positions of the visitors in a path to the goal node, from the
        start to (and including) the goal node.

    Raises
    ------
    RuntimeError
        If the path to the goal node is not valid. In normal usage, this should
        never occur.
    """
    points: list[Point] = []
    visitor: Node | None = goal_node
    while visitor is not start_node:
        if visitor is None:
            raise RuntimeError("no path was found to the destination")

        points.append(visitor.value)
        visitor = visitor.visitor

    points.reverse()
    for point in points:
        yield point


def _search(
    search_queue: list[_SearchNode],
    start_node: Node,
    goal_node: Node,
    boundary_line_segments: Iterable[LineSegment],
) -> bool:
    """
    Search for the goal node in the graph. Mutates the search queue passed
    in and the visitor attribute of the graph nodes.

    Parameters
    ----------
    search_queue : list[_SearchNode]
        A min priority queue used to search for the goal node. Must already
        contain the starting nodes in the graph in the correct order.
    start_node:
        The start node.
    goal_node : Node
        The goal node.
    boundary_line_segments : Iterable[LineSegment]
        The line segments forming the flight area boundary.

    Returns
    -------
    bool
        Whether the search was successful.
    """

    while search_queue:
        search_node: _SearchNode = heapq.heappop(search_queue)
        curr_distance_so_far: float = search_node.distance_so_far
        visitor: Node | None = search_node.visitor
        node: Node = search_node.node

        if node.visitor is not None:
            continue

        # visitor is not None needed to satisfy mypy
        if visitor == start_node or node == goal_node and visitor is not None:
            shrunk_straight_path: LineSegment = _shrink_line_segment(
                LineSegment(visitor.value, node.value)
            )
            if any(
                shrunk_straight_path.intersects(boundary_line_segment)
                for boundary_line_segment in boundary_line_segments
            ):
                continue

        node.visitor = visitor

        if node == goal_node:
            return True

        visitor = node
        for node, weight in node.edges.items():
            if node.visitor is not None:
                continue

            distance_so_far: float = curr_distance_so_far + weight
            heapq.heappush(
                search_queue,
                _SearchNode(
                    distance_so_far + LineSegment(node.value, goal_node.value).length(),
                    distance_so_far,
                    visitor,
                    node,
                ),
            )

    return False


def shortest_path_between(src: Point, dst: Point, boundary: Iterable[Node]) -> Iterable[Point]:
    """
    Find the shortest path between two points given a graph with all possible
    paths between boundary points.

    Parameters
    ----------
    src : Point
        The point we're currently at.
    dst : Point
        The point to move to.
    boundary: Iterable[Node]
        Graph nodes with all the boundary points and possible paths between
        those points. The points must be in order, but it does not matter
        whether they are in clockwise or counterclockwise order.

    Yields
    -------
    Point
        The next point to move to in order to get to the destination using
        the shorted path.

    Raises
    ------
    RuntimeError
        If no path was found to the destination. In normal usage, this should
        never occur.
    """
    boundary_nodes: list[Node] = list(boundary)
    boundary_line_segments: Iterable[LineSegment] = list(
        LineSegment.from_points((node.value for node in boundary_nodes), True)
    )

    straight_path: LineSegment = LineSegment(src, dst)
    if not any(
        straight_path.intersects(boundary_line_segment)
        for boundary_line_segment in boundary_line_segments
    ):
        yield dst
        return

    # We use the A* search algorithm

    start_node: Node = Node(src)
    goal_node: Node = Node(dst)
    search_queue: list[_SearchNode] = []

    for boundary_node in boundary_nodes:
        boundary_node.visitor = None

        straight_path = LineSegment(boundary_node.value, dst)
        distance_to_goal: float = straight_path.length()
        boundary_node.connect(goal_node, distance_to_goal)

        straight_path = LineSegment(src, boundary_node.value)
        distance_from_start: float = straight_path.length()
        heapq.heappush(
            search_queue,
            _SearchNode(
                distance_from_start + distance_to_goal,
                distance_from_start,
                start_node,
                boundary_node,
            ),
        )

    success: bool = _search(search_queue, start_node, goal_node, boundary_line_segments)

    for boundary_node in boundary_nodes:
        boundary_node.disconnect(goal_node)

    if success:
        yield from _visitors(start_node, goal_node)
    else:
        raise RuntimeError("no path was found to the destination")


def create_pathfinding_graph(boundary: Iterable[Point], safety_margin: float) -> list[Node]:
    """
    Create a graph suitable to be used as the boundary graph when pathfinding.

    Parameters
    ----------
    boundary : Iterable[Point]
        The vertices of the boundary. They must be in order, but it does not
        matter whether they are in clockwise or counterclockwise order.
    safety_margin : float
        How far to move the boundary vertices inward. The units are the same
        as the units for `boundary`.

    Returns
    -------
    list[Node]
        A list of graph nodes constituting the pathfinding graph.
    """
    points: list[Point] = list(boundary)
    points_moved_inward: list[Point] = []
    for point, line_segment_1, line_segment_2 in zip(
        points,
        LineSegment.from_points([points[-1]] + points[:-1], True),
        LineSegment.from_points(points, True),
    ):
        # line_segment_1 and line_segment_2 are the line segments connecting
        #   this point to the adjacent points

        vec_1: Point = line_segment_1.p_1 - line_segment_1.p_2
        vec_2: Point = line_segment_2.p_2 - line_segment_2.p_1
        vec_1 /= vec_1.distance_from_origin()
        vec_2 /= vec_2.distance_from_origin()

        perp_vec_1: Point = Point(-vec_1.y, vec_1.x)

        inward_diff: Point = vec_1 + vec_2
        if inward_diff.distance_from_origin() < 1e-3:
            inward_diff = perp_vec_1
        inward_diff /= inward_diff.distance_from_origin()

        if not (point + 1e-3 * inward_diff).is_inside_shape(points):
            inward_diff *= -1.0

        # The length of inward_diff in the direction of perp_vec_1
        length_divisor: float = abs(inward_diff.dot(perp_vec_1) / perp_vec_1.distance_from_origin())
        inward_diff /= length_divisor

        inward_diff *= safety_margin
        points_moved_inward.append(point + inward_diff)

    boundary_line_segments: list[LineSegment] = list(
        LineSegment.from_points(points_moved_inward, True)
    )

    # Rather inefficient
    # Thankfully, there shouldn't be too many boundary vertices
    nodes: list[Node] = [Node(point) for point in points_moved_inward]
    for node_1 in nodes:
        for node_2 in nodes:
            if node_1 == node_2:
                continue

            straight_path: LineSegment = LineSegment(node_1.value, node_2.value)
            midpoint: Point = (straight_path.p_1 + straight_path.p_2) / 2

            direction: Point = straight_path.p_2 - straight_path.p_1
            direction /= direction.distance_from_origin()
            shrunk_straight_path: LineSegment = LineSegment(
                straight_path.p_1 + 1e-3 * direction, straight_path.p_2 - 1e-3 * direction
            )

            if straight_path in boundary_line_segments or (
                midpoint.is_inside_shape(points_moved_inward)
                and not any(
                    shrunk_straight_path.intersects(boundary_line_segment)
                    for boundary_line_segment in boundary_line_segments
                )
            ):
                node_1.connect(node_2, straight_path.length())

    return nodes
