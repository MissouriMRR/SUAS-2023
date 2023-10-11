"""Tests the state machine."""
import logging
import asyncio

from state_machine.flight_manager import process_test
from flight.test_files.golf_waypoint_test import run

logging.basicConfig(level=logging.INFO)
process_test()
# asyncio.run(run())


# asyncio.run(test()) for the other one
