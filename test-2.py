"""Tests the state machine."""

import asyncio
import logging

from state_machine.test2 import process_test

logging.basicConfig(level=logging.INFO)
process_test()


#asyncio.run(test()) for the other one

