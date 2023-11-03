"""Defines classes for points and line segments and some helper functions"""

from dataclasses import dataclass
import math


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
    """

    x: float
    y: float

    def __sub__(self, rhs: "Point") -> "Point":
        return Point(self.x - rhs.x, self.y - rhs.y)

    def __mul__(self, rhs: float) -> "Point":
        return Point(self.x * rhs, self.y * rhs)

    def __rmul__(self, lhs: float) -> "Point":
        return Point(lhs * self.x, lhs * self.y)


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
        Calculate the length of this line segment..

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
