"""
This module implements the Vector3 class
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Iterator, overload

import mavsdk.offboard
import mavsdk.telemetry


@dataclass(slots=True)
class Vector3:
    """
    Represents 3D vector in physical space;
    units depend on context

    Attributes
    ----------
    north : float
        The north component of this vector
    east : float
        The east component of this vector
    down : float
        The down component of this vector
    length: float
    """

    north: float
    east: float
    down: float

    @overload
    def __init__(self, north: float, east: float, down: float):
        ...

    @overload
    def __init__(self, north: float):
        ...

    def __init__(self, north: float, east: float | None = None, down: float | None = None):
        self.north = north
        self.east = north if east is None else east
        self.down = north if down is None else down

    @classmethod
    def from_mavsdk_velocityned(cls, velocity: mavsdk.telemetry.VelocityNed) -> Vector3:
        """
        Factory method accepting a mavsdk.telemetry.VelocityNed object

        Parameters
        ----------
        velocity : mavsdk.telemetry.VelocityNed
            A velocity (NED) from MAVSDK

        Returns
        -------
        A new Vector3 object, using meters for units
        """

        return cls(velocity.north_m_s, velocity.east_m_s, velocity.down_m_s)

    def to_mavsdk_velocitynedyaw(
        self, yaw_deg: float | None = None
    ) -> mavsdk.offboard.VelocityNedYaw:
        """
        Converts this Vector3 object to a mavsdk.offboard.VelocityNedYaw
        object; this vector must use meters for units

        Parameters
        ----------
        yaw_deg : float | None = None
            The yaw, in degrees, of the resulting object; north is 0 degrees,
            with yaw increasing clockwise looking down; this value will be
            calculated from the north and east components of this vector
            if not provided

        Returns
        -------
        The equivalent mavsdk.offboard.VelocityNedYaw object
        """

        if yaw_deg is None:
            yaw_deg = math.degrees(math.atan2(self.east, self.north))

        return mavsdk.offboard.VelocityNedYaw(self.north, self.east, self.down, yaw_deg)

    def __hash__(self) -> int:
        big_hash: int = ((hash(self.north) * 3) + hash(self.east)) * 3 + hash(self.down)
        return big_hash & 0xFFFF_FFFF_FFFF_FFFF

    # Implement unpacking
    def __iter__(self) -> Iterator[float]:
        return iter((self.north, self.east, self.down))

    # Implement **kwargs unpacking

    def keys(self) -> list[str]:
        """
        Gets a list of keys for **kwargs unpacking

        Returns
        -------
        The list ["north", "east", "down"]
        """
        return ["north", "east", "down"]

    def __getitem__(self, key: str) -> float:
        match key:
            case "north":
                return self.north
            case "east":
                return self.east
            case "down":
                return self.down
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
        return math.hypot(self.north, self.east, self.down)

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
        return Vector3(-self.north, -self.east, -self.down)

    def __add__(self, rhs: Vector3) -> Vector3:
        return Vector3(
            self.north + rhs.north,
            self.east + rhs.east,
            self.down + rhs.down,
        )

    def __sub__(self, rhs: Vector3) -> Vector3:
        return self + -rhs

    def __mul__(self, rhs: Vector3 | float) -> Vector3:
        if isinstance(rhs, Vector3):
            return Vector3(
                self.north * rhs.north,
                self.east * rhs.east,
                self.down * rhs.down,
            )
        return Vector3(self.north * rhs, self.east * rhs, self.down * rhs)

    def __rmul__(self, lhs: float) -> Vector3:
        return self * lhs

    def __truediv__(self, rhs: Vector3 | float) -> Vector3:
        if isinstance(rhs, Vector3):
            return Vector3(
                self.north / rhs.north,
                self.east / rhs.east,
                self.down / rhs.down,
            )
        return Vector3(self.north / rhs, self.east / rhs, self.down / rhs)
