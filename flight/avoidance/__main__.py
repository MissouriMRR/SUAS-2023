"""
Tests this package
"""

import asyncio
import subprocess

from . import test


def main() -> None:
    """Run tests"""

    with subprocess.Popen(["bash", "avoidance/opensitlmultiple.sh"]) as _:
        pass

    asyncio.run(test.run())


main()
