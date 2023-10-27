"""Implement the behavior of the Waypoint state."""
import asyncio
import logging

from flight.extract_gps import extract_gps, GPSData
from flight.extract_gps import Waypoint as Waylist

from flight.waypoint.goto import move_to

from state_machine.states.airdrop import Airdrop
from state_machine.states.odlc import ODLC
from state_machine.states.state import State
from state_machine.states.waypoint import Waypoint


async def run(self: Waypoint) -> State:
    """
    Run method implementation for the Waypoint state.

    This method instructs the drone to navigate to a specified waypoint and
    transitions to the Airdrop or ODLC State.

    Returns
    -------
    Airdrop : State
        The next state after successfully reaching the specified waypoint and
        initiating the Airdrop process.
    ODLC : State
        The next state after successfully reaching the specified waypoint and
        initiating the ODLC process.

    Notes
    -----
    This method is responsible for guiding the drone to a predefined waypoint in its flight path.
    Upon reaching the waypoint, it transitions the drone to the Land state to initiate landing.

    """

    gps_path: str = "flight/data/waypoint_data.json"

    try:
        logging.info("Waypoint state running")
        print("Moving to waypoint")

        gps_dict: GPSData = extract_gps(gps_path)
        waypoints: list[Waylist] = gps_dict["waypoints"]

        for waypoint in waypoints:
            # use 5/6 as a fast parameter to get 25m with plenty of leeway while being fast
            await move_to(self.drone.system, waypoint[0], waypoint[1], waypoint[2], 5 / 6)

        if self.drone.odlc_scan:
            return ODLC(self.drone)
        return Airdrop(self.drone)

    except asyncio.CancelledError as ex:
        logging.error("Waypoint state canceled")
        raise ex
    finally:
        pass


# Set the run_callable attribute of the Waypoint class to the run function
Waypoint.run_callable = run
