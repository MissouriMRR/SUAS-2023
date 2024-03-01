"""Implements the behavior of the Airdrop state."""

import asyncio
import logging
import json

from state_machine.states.airdrop import Airdrop
from state_machine.states.land import Land
from state_machine.states.waypoint import Waypoint
from state_machine.states.state import State
from state_machine.states.land import Land

from flight.maestro.air_drop import AirdropControl
from flight.waypoint.goto import move_to


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
        if self.drone.address == "serial:///dev/ttyUSB0:921600":
            # setup airdrop
            airdrop = AirdropControl()

        with open("flight/data/output.json", encoding="utf8") as output:
            bottle_locations = json.load(output)

        with open("flight/data/bottles.json", encoding="utf8") as output:
            cylinders = json.load(output)

        # For the amount of bottles there are...
        bottle_num: int = self.drone.num + 1
        logging.info("Bottle drop started")

        # Set initial value for lowest distance so we can compare

        bottle_loc: dict[str, float] = bottle_locations[str(self.drone.bottle_num)]

        # Move to the nearest bottle
        await move_to(self.drone.system, bottle_loc["latitude"], bottle_loc["longitude"], 80, 1)

        logging.info("Starting bottle drop")
        if self.drone.address == "serial:///dev/ttyUSB0:921600":
            await airdrop.drop_bottle(self.drone.servo_num)

        await asyncio.sleep(
            15
        )  # This will need to be changed based on how long it takes to drop the bottle

        logging.info("-- Airdrop done!")

        self.drone.bottle_num = self.drone.bottle_num + 1
        if self.drone.servo_num == 2:
            self.drone.servo_num = 0
        else:
            self.drone.servo_num = self.drone.servo_num + 1

        continuerun: bool = False

        for cylinder in cylinders:
            if cylinder["Loaded"]:
                continuerun = True

        if continuerun:
            return Waypoint(self.drone, self.flight_settings)
        return Land(self.drone, self.flight_settings)

    except asyncio.CancelledError as ex:
        logging.error("Airdrop state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Airdrop class to the run function
Airdrop.run_callable = run
