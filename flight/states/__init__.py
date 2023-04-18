"""Initialization File for state exporting"""

from typing import Type, Dict
from enum import Enum

from flight.states.state import (
    State,
    Start,
    PreProcess,
    Takeoff,
    Waypoints,
    ODLC,
    AirDrop,
    Land,
    Final,
)

# Used to export the various state modules under these given names
STATES: Dict[
    str, Type[Start | PreProcess | Takeoff | Waypoints | ODLC | AirDrop | Land | Final]
] = {
    "Start_State": Start,
    "Pre_Process": PreProcess,
    "Takeoff": Takeoff,
    "Waypoints": Waypoints,
    "ODLC_Scanning": ODLC,
    "Air_Drop": AirDrop,
    "Land": Land,
    "Final_State": Final,
}


class StateEnum(str, Enum):
    """
    A string enumeration of the states in the flight state machine.
    """

    START_STATE = "Start_State"
    PRE_PROCESS = "Pre_Process"
    TAKEOFF = "Takeoff"
    WAYPOINTS = "Waypoints"
    ODLC_SCANNING = "ODLC_Scanning"
    AIR_DROP = "Air_Drop"
    LAND = "Land"
    FINAL_STATE = "Final_State"
