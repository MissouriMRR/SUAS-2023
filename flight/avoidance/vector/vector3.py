"""
This module implements the Vector3 class
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Iterator, overload


@dataclass(slots=True)
class Vector3:
    """
    A 3D vector

    Attributes
    ----------
    x : float
        The x component of this vector
    y : float
        The y component of this vector
    z : float
        The z component of this vector
    length: float
    """

    x: float
    y: float
    z: float

    @overload
    def __init__(self, x: float, y: float, z: float):
        ...

    @overload
    def __init__(self, x: float):
        ...

    def __init__(self, x: float, y: float | None = None, z: float | None = None):
        self.x = x
        self.y = x if y is None else y
        self.z = x if z is None else z

    def __hash__(self) -> int:
        big_hash: int = ((hash(self.x) * 3) + hash(self.y)) * 3 + hash(self.z)
        return big_hash & 0xFFFF_FFFF_FFFF_FFFF

    # Implement unpacking
    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y, self.z))

    # Implement **kwargs unpacking

    def keys(self) -> list[str]:
        """
        Gets a list of keys for **kwargs unpacking

        Returns
        -------
        The list ['x', 'y', 'z']
        """
        return ["x", "y", "z"]

    def __getitem__(self, key: str) -> float:
        match key:
            case "x":
                return self.x
            case "y":
                return self.y
            case "z":
                return self.z
            case _:
                raise KeyError(f"{key} is not a valid key of {type(self).__name__}")

    @property
    def length(self) -> float:
        """
        Calculates the magnitude of this vector

        Returns
        -------
        The magnitude of this vector
        """
        return math.hypot(self.x, self.y, self.z)

    def normalized(self) -> Vector3:
        """
        Creates a normalized version of this vector

        Returns
        -------
        A vector with the same direction as this vector
        and a magnitude of 1.0 (within floating-point error)
        """
        return self / self.length

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def __add__(self, rhs: Vector3) -> Vector3:
        return Vector3(
            self.x + rhs.x,
            self.y + rhs.y,
            self.z + rhs.z,
        )

    def __sub__(self, rhs: Vector3) -> Vector3:
        return self + -rhs

    def __mul__(self, rhs: Vector3 | float) -> Vector3:
        if isinstance(rhs, Vector3):
            return Vector3(
                self.x * rhs.x,
                self.y * rhs.y,
                self.z * rhs.z,
            )
        return Vector3(self.x * rhs, self.y * rhs, self.z * rhs)

    def __rmul__(self, lhs: float) -> Vector3:
        return self * lhs

    def __truediv__(self, rhs: Vector3 | float) -> Vector3:
        if isinstance(rhs, Vector3):
            return Vector3(
                self.x / rhs.x,
                self.y / rhs.y,
                self.z / rhs.z,
            )
        return Vector3(self.x / rhs, self.y / rhs, self.z / rhs)
