"""Tests the state machine."""

import asyncio
import logging

from .test import test


def main() -> None:
    """The main function."""
    cancel_delay = float(input("Enter the number of seconds to run the state machine for: "))

    logging.basicConfig(level=logging.INFO)
    asyncio.run(test(cancel_delay))


main()
