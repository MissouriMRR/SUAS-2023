#!/usr/bin/env python3
"""
Main runnable file for the codebase

If running for competition, make sure that the following is set:
- Bottle data in vision/competition_inputs/bottle_data.json
- Waypoints in flight/data/waypoint_data.json
"""

from __future__ import annotations

import asyncio
import logging
from logging.handlers import QueueListener
import sys
from multiprocessing import Queue
from state_machine.flight_manager import FlightManager
from logger import init_logger, worker_configurer

if __name__ == "__main__":
    # Run multiprocessing function
    try:
        queue: Queue[str] = Queue()
        worker_configurer(queue)
        listener: QueueListener = init_logger(queue)
        listener.start()

        SIM_FLAG: bool = False
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting processes")
        flight_manager: FlightManager = FlightManager()
        if "-s" in sys.argv:
            SIM_FLAG = True
        asyncio.run(flight_manager.run_manager(SIM_FLAG))
    finally:
        logging.info("Done!")
