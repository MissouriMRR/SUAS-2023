#!/usr/bin/env python3
"""
Main runnable file for the codebase

If running for competition, make sure that the following is set:
- Bottle data in vision/competition_inputs/bottle_data.json
- Waypoints in flight/data/waypoint_data.json
"""

import logging

from state_machine.flight_manager import FlightManager


if __name__ == "__main__":
    # Run multiprocessing function
    try:
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting processes")
        flight_manager: FlightManager = FlightManager()
        flight_manager.start_manager()
    finally:
        logging.info("Done!")
