"""
Defines and implements the Velocity class used in obstacle_avoidance.py
"""

from __future__ import annotations
from dataclasses import dataclass
import math
from typing import overload

import mavsdk.telemetry


@dataclass(frozen=True, slots=True)
class Velocity:
    """
    A velocity in 3D space

    Attributes
    ----------
    north_vel : float
        Eastward velocity in meters per second
    east_vel : float
        Northward velocity in meters per second
    down_vel : float
        Downward velocity in meters per second
    """

    north_vel: float
    east_vel: float
    down_vel: float

    @classmethod
    def from_mavsdk_velocityned(cls, velocity: mavsdk.telemetry.VelocityNed) -> Velocity:
        """
        Factory method accepting a mavsdk.telemetry.VelocityNed object

        Parameters
        ----------
        velocity : mavsdk.telemetry.VelocityNed
            A velocity (NED) from MAVSDK

        Returns
        -------
        A new Velocity object
        """

        return cls(velocity.north_m_s, velocity.east_m_s, velocity.down_m_s)

    def __add__(self, rhs: Velocity) -> Velocity:
        return Velocity(
            self.north_vel + rhs.north_vel,
            self.east_vel + rhs.east_vel,
            self.down_vel + rhs.down_vel,
        )

    def __sub__(self, rhs: Velocity) -> Velocity:
        return Velocity(
            self.north_vel - rhs.north_vel,
            self.east_vel - rhs.east_vel,
            self.down_vel - rhs.down_vel,
        )

    @overload
    def __mul__(self, rhs: float) -> Velocity:
        ...

    @overload
    def __mul__(self, rhs: Velocity) -> Velocity:
        ...

    def __mul__(self, rhs: float | Velocity) -> Velocity:
        if isinstance(rhs, float):
            rhs = Velocity(rhs, rhs, rhs)

        return Velocity(
            self.north_vel * rhs.north_vel,
            self.east_vel * rhs.east_vel,
            self.down_vel * rhs.down_vel,
        )

    def __rmul__(self, lhs: float) -> Velocity:
        return self.__mul__(lhs)

    @overload
    def __truediv__(self, rhs: float) -> Velocity:
        ...

    @overload
    def __truediv__(self, rhs: Velocity) -> Velocity:
        ...

    def __truediv__(self, rhs: float | Velocity) -> Velocity:
        if isinstance(rhs, float):
            rhs = Velocity(rhs, rhs, rhs)

        return Velocity(
            self.north_vel / rhs.north_vel,
            self.east_vel / rhs.east_vel,
            self.down_vel / rhs.down_vel,
        )

    def speed(self) -> float:
        """
        Converts a Velocity object to a speed value

        Returns
        -------
        The length of this velocity vector
        """

        return math.hypot(self.north_vel, self.east_vel, self.down_vel)

    def normalized(self) -> Velocity:
        """
        Normalizes a Velocity object

        Returns
        -------
        A new Velocity object with speed 1 pointing in the same direction
        """

        return self / self.speed()
