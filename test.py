"""Tests the state machine."""

import asyncio
import logging

from state_machine.test import test

logging.basicConfig(level=logging.INFO)
asyncio.run(test(10.0))
