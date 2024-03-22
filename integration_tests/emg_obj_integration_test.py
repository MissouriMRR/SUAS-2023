"""Runs emergent object code for testing purposes"""

import asyncio
import logging
import sys

from state_machine.flight_manager import FlightManager


async def run_test(_sim: bool) -> None:  # Temporary fix for unused variable
    """
    Initialize and run the flight manager for the emergent object
    integration test.

    Parameters
    ----------
    _sim : bool
        Specifies whether to run the state machine in simulation mode.
    """
    # Output logging info to stdout
    logging.basicConfig(filename="/dev/stdout", level=logging.INFO)

    path_data_path: str = "flight/data/waypoint_data.json" if _sim else "flight/data/golf_data.json"

    flight_manager: FlightManager = FlightManager()
    await flight_manager.run_manager(
        _sim, path_data_path, skip_waypoint=True, standard_object_count=0
    )


if __name__ == "__main__":
    print("Pass argument --sim to enable the simulation flag.")
    print("When the simulation flag is not set, golf data is used.")
    print(
        "Running in simulation mode probably won't work, but is supported by the integration test."
    )
    print()
    asyncio.run(run_test("--sim" in sys.argv))
