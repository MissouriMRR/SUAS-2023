"""Tests the state machine."""

import asyncio

from .test import test


def main() -> None:
    """The main function."""
    asyncio.run(test())


main()
