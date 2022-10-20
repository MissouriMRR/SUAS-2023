"""
Defines and implements the Velocity class used in obstacle_avoidance.py
"""

from dataclasses import dataclass

import mavsdk.telemetry


@dataclass
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
    def from_mavsdk_velocityned(cls, velocity: mavsdk.telemetry.VelocityNed) -> "Velocity":
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
