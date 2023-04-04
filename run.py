#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import logging

from flight_manager import FlightManager
from flight.state_settings import StateSettings


if __name__ == "__main__":
    # Run multiprocessing function
    try:
        state_settings: StateSettings = StateSettings()
        flight_manager: FlightManager = FlightManager(state_settings)
        flight_manager.main()
    except:
        logging.exception("Unfixable error detected")
