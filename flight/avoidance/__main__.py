"""
Tests this package using PX4 Autopilot and the Gazebo simulator
"""

import asyncio
import subprocess

from . import test


def main() -> None:
    """Run tests"""

    with subprocess.Popen(["bash", "avoidance/opensitlmultiple.sh"]):
        pass

    asyncio.run(test.run())


main()
