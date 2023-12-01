"""Implements the behavior of the Airdrop state."""
import asyncio
import logging
import json

from state_machine.states.airdrop import Airdrop
from state_machine.states.waypoint import Waypoint
from state_machine.states.state import State

from flight.airdrop import AirdropControl
from flight.waypoint.goto import move_to

from mavsdk import telemetry


async def run(self: Airdrop) -> State:
    """
    Implements the run method for the Airdrop state.

    Returns
    -------
    Waypoint : State
        The next state after the drone has successfully completed the Airdrop.

    Notes
    -----
    This method is responsible for initiating the Airdrop process of the drone and transitioning
    it back to the Waypoint state.
    """
    try:
        logging.info("Airdrop")

        # setup airdrop
        airdrop = AirdropControl()

        with open("flight/data/output.json", encoding="utf8") as output:
            bottle_locations = json.load(output)

        # For the amount of bottles there are...
        bottle_num: int = self.drone.num + 1
        logging.info("Bottle drop #", bottle_num, "started")
        # Set initial value for lowest distance so we can compare

        bottle_loc: dict[str, float] = bottle_locations[str(bottle_num)]

        # Get the drones current position
        async for position in self.drone.system.telemetry.position():
            current_location: telemetry.Position = position
            break

        # Move to the nearest bottle
        await move_to(self.drone.system, bottle_loc["latitude"], bottle_loc["longitude"], 80, 1)
        await airdrop.drop_bottle(self.drone.servo_num)
        await asyncio.sleep(
            15
        )  # This will need to be changed based on how long it takes to drop the bottle

        logging.info("-- Airdrop done!")

        self.drone.num = self.drone.num + 1
        if self.drone.servo_num == 2:
            servo_num = 0
        else:
            servo_num = servo_num + 1

        return Waypoint(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Airdrop state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Airdrop class to the run function
Airdrop.run_callable = run
