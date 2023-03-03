"""
This package implements obstacle avoidance functions
for a MAVSDK drone
"""

from .avoidance_goto import goto_with_avoidance
from .obstacle_avoidance import calculate_avoidance_velocity, Point, InputPoint, Velocity
