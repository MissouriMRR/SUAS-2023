"""
Defines and implements the Velocity class used in obstacle_avoidance.py
"""

from __future__ import annotations
from dataclasses import dataclass
import math

import mavsdk.offboard
import mavsdk.telemetry


@dataclass(slots=True)
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

    def to_mavsdk_velocitynedyaw(self) -> mavsdk.offboard.VelocityNedYaw:
        """
        Converts this Velocity object to a mavsdk.offboard.VelocityNedYaw
        object

        Returns
        -------
        The equivalent mavsdk.offboard.VelocityNedYaw object
        """

        yaw_deg: float = math.degrees(math.atan2(self.east_vel, self.north_vel))

        return mavsdk.offboard.VelocityNedYaw(self.north_vel, self.east_vel, self.down_vel, yaw_deg)

    def __neg__(self) -> Velocity:
        return Velocity(-self.north_vel, -self.east_vel, -self.down_vel)

    def __add__(self, rhs: Velocity) -> Velocity:
        return self + -rhs

    def __sub__(self, rhs: Velocity) -> Velocity:
        return Velocity(
            self.north_vel - rhs.north_vel,
            self.east_vel - rhs.east_vel,
            self.down_vel - rhs.down_vel,
        )

    def __mul__(self, rhs: float | Velocity) -> Velocity:
        if isinstance(rhs, Velocity):
            return Velocity(
                self.north_vel * rhs.north_vel,
                self.east_vel * rhs.east_vel,
                self.down_vel * rhs.down_vel,
            )

        return Velocity(self.north_vel * rhs, self.east_vel * rhs, self.down_vel * rhs)

    def __rmul__(self, lhs: float) -> Velocity:
        return self * lhs

    def __truediv__(self, rhs: float | Velocity) -> Velocity:
        if isinstance(rhs, Velocity):
            return Velocity(
                self.north_vel / rhs.north_vel,
                self.east_vel / rhs.east_vel,
                self.down_vel / rhs.down_vel,
            )

        return Velocity(self.north_vel / rhs, self.east_vel / rhs, self.down_vel / rhs)

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
