#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import logging
import sys
from state_machine.flight_manager import FlightManager

if __name__ == "__main__":
    # Run multiprocessing function
    try:
        simflag: bool = False
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting processes")
        flight_manager: FlightManager = FlightManager()
        if "-s" in sys.argv:
            simflag = True
        flight_manager.start_manager(simflag)
    finally:
        logging.info("Done!")
