"""Initialization File for state exporting"""
from typing import Dict
from flight.states.state import State
from flight.states.start import Start
from flight.states.preprocess import PreProcess
from flight.states.takeoff import Takeoff
from flight.states.waypoints import Waypoints
from flight.states.odlcs import ODLC
from flight.states.airdrop import AirDrop
from flight.states.land import Land
from flight.states.final import Final

""" The STATES dictionary is used to export the various state modules under these given names """
STATES: Dict[str, State] = {
    "Start_State": Start,
    "Pre_Process": PreProcess,
    "Takeoff": Takeoff,
    "Waypoints": Waypoints,
    "ODLC_Scanning": ODLC,
    "Air_Drop": AirDrop,
    "Land": Land,
    "Final_State": Final
}
