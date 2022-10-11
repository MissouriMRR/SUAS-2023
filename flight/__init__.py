"""Initialization File for state importing"""
from typing import Dict
from states.state import State
from states.start import Start
from states.preprocess import PreProcess
from states.takeoff import Takeoff
from states.waypoints import Waypoints
from states.odlcs import ODLC
from states.airdrop import AirDrop
from states.land import Land
from states.final import Final

STATES: Dict[str, State] = {
    "Start State": Start,
    "Pre-Process": PreProcess,
    "Takeoff": Takeoff,
    "Waypoints": Waypoints,
    "ODLC Scanning": ODLC,
    "Air Drop": AirDrop,
    "Land": Land,
    "Final State": Final,
}
