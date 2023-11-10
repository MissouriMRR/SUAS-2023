#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import logging
import sys
from state_machine.flight_manager import FlightManager

if __name__ == "__main__":
    # Run multiprocessing function
    try:
        sim_flag: bool = False
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting processes")
        flight_manager: FlightManager = FlightManager()
        if "-s" in sys.argv:
            sim_flag = True
        flight_manager.start_manager(sim_flag)
    finally:
        logging.info("Done!")
