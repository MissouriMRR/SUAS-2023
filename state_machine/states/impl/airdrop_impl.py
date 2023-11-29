"""Implements the behavior of the Airdrop state."""
import asyncio
import logging

from state_machine.states.airdrop import Airdrop
from state_machine.states.waypoint import Waypoint
from state_machine.states.state import State

from flight.airdrop import AirdropControl
from flight.goto import move_to


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

        # For the amount of bottles there are...
        num: int = 0
        bottle_num: int = num+1
        servo_num: int
        logging.info("Bottle drop #", bottle_num, "started")
        # Set initial value for lowest distance so we can compare

        # Get the drones current position
        async for position in drone.telemetry.position():
            current_location: telemetry.Position = position
            break

        # Move to the nearest bottle
        await move_to(drone, bottle_loc["latitude"], bottle_loc["longitude"], 80, 1)
        await airdrop.drop_bottle(servo_num)
        await asyncio.sleep(
            15
        )  # This will need to be changed based on how long it takes to drop the bottle
        # Remove the bottle location from the dictionary
        bottle_locations.pop(bottle_num)
        logging.info("-- Airdrop done!")

        return Waypoint(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Airdrop state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Airdrop class to the run function
Airdrop.run_callable = run
