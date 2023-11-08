"""Defines classes for points and line segments and some helper functions"""

from dataclasses import dataclass
import math
from typing import Iterable, Iterator


def lerp(x: float, y: float, position: float) -> float:
    """
    Linearly interpolate between two values.

    Parameters
    ----------
    x : float
        The first value.
    y : float
        The second value.
    position : float
        The normalized distance between the two values to linearly interpolate
        between. A distances of 0 corresponds to the value `x`, and 1
        corresponds to `y`.

    Returns
    -------
    float
        The interpolated value.
    """
    return (1 - position) * x + position * y


def inverse_lerp(x: float, y: float, value: float) -> float:
    """
    Performs the inverse of linear interpolation

    Parameters
    ----------
    x : float
        The first value.
    y : float
        The second value.
    value : float
        The value for which to find the normalized distance between the values
        `x` and `y`. The value `x` corresponds to a distance of 0, and `y`
        corresponds to 1.

    Returns
    -------
    float
        How far between `x` and `y` `value` is.
    """
    return (value - x) / (y - x)


@dataclass(slots=True)
class Point:
    """
    A point in 2D space.

    Attributes
    ----------
    x : float
        The x-coordinate.
    y : float
        The y-coordinate.

    Methods
    -------
    is_inside_shape(vertices: Iterable[Point]) -> bool
        Tests whether a point is inside a shape defined by some vertices.
    """

    x: float
    y: float

    def __sub__(self, rhs: "Point") -> "Point":
        return Point(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs: float) -> "Point":
        return Point(self.x * rhs, self.y * rhs)

    def __rmul__(self, lhs: float) -> "Point":
        return Point(lhs * self.x, lhs * self.y)

    def is_inside_shape(self, vertices: Iterable["Point"]) -> bool:
        """
        Tests whether a point is inside a shape defined by some vertices.

        Parameters
        ----------
        vertices : Iterable[Point]
            The vertices of the shape. They must be in order, but it does not
            matter whether they are in clockwise or counterclockwise order.

        Returns
        -------
        bool
            Whether the point is inside the shape according the nonzero winding
            rule.
        """
        # Please see https://en.wikipedia.org/wiki/Nonzero-rule
        winding_number: int = 0
        for line_segment in LineSegment.from_points(vertices, True):
            y_1: float = line_segment.p_1.y
            y_2: float = line_segment.p_2.y
            if y_1 == y_2:
                continue

            if not min(y_1, y_2) <= self.y < max(y_1, y_2):
                continue

            x_1: float = line_segment.p_1.x
            x_2: float = line_segment.p_2.x
            if lerp(x_1, x_2, inverse_lerp(y_1, y_2, self.y)) > self.x:
                continue

            if y_1 < y_2:
                winding_number += 1
            else:
                winding_number -= 1

        return winding_number != 0


@dataclass(slots=True)
class LineSegment:
    """
    A line segment in 2D space.

    Attributes
    ----------
    p_1 : Point
        The first endpoint.
    p_2 : Point
        The second endpoint.

    Methods
    -------
    length() -> float
        Calculate the length of this line segment.
    intersects(other: LineSegment) -> bool
        Checks whether this line segment intersects another line segment.
    """

    p_1: Point
    p_2: Point

    def length(self) -> float:
        """
        Calculate the length of this line segment.

        Returns
        -------
        float
            The length of this line segment.
        """
        diff: Point = self.p_2 - self.p_1
        return math.hypot(diff.x, diff.y)

    def intersects(self, other: "LineSegment") -> bool:
        """
        Check whether this line segment intersects another line segment

        Parameters
        ----------
        other : LineSegment
            The other line segment.

        Returns
        -------
        bool
            True if the two line segments intersect, otherwise False.
        """
        diff: Point = self.p_2 - self.p_1
        val1: float = diff.x * (other.p_1.y - self.p_1.y) - diff.y * (other.p_1.x - self.p_1.x)
        val2: float = diff.x * (other.p_2.y - self.p_1.y) - diff.y * (other.p_2.x - self.p_1.x)

        if val1 * val2 > 0:
            # The two endpoints of the other line segment are on the same side
            #   of this line.
            return False

        t_1: float = inverse_lerp(val1, val2, 0.0)
        # The intersection point
        point: Point = Point(
            lerp(other.p_1.x, other.p_2.x, t_1),
            lerp(other.p_1.y, other.p_2.y, t_1),
        )
        # How far the intersection point would be along this line segment
        t_2: float = (diff.x * (point.x - self.p_1.x) + diff.y * (point.y - self.p_1.y)) / (
            diff.x * diff.x + diff.y * diff.y
        )

        return 0 <= t_2 <= 1

    @classmethod
    def from_points(
        cls, points: Iterable[Point], connect_last_to_first: bool
    ) -> Iterable["LineSegment"]:
        """
        Connect some points with line segments

        Parameters
        ----------
        points : Iterable[Point]
            The points to connect.
        connect_last_to_first : bool
            Whether to connect the last point to the first point.

        Yields
        -------
        LineSegment
            Line segments connecting the points in order. The first point is
            connected to the second point, the second to the third, and so on.
        """
        points_iter: Iterator[Point] = iter(points)
        try:
            first_point: Point = next(points_iter)
        except StopIteration:
            return

        prev_point: Point = first_point
        for point in points_iter:
            yield cls(prev_point, point)
            prev_point = point

        if connect_last_to_first:
            yield cls(prev_point, first_point)
