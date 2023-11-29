"""Implements the behavior of the Airdrop state."""
import asyncio
import logging

from state_machine.states.airdrop import Airdrop
from state_machine.states.waypoint import Waypoint
from state_machine.states.state import State


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

        # code for Airdrop logic

        # setup airdrop
        airdrop = AirdropControl()

        # For the amount of bottles there are...
        for num in range(len(bottle_locations)):
            logging.info("Bottle drop #", num + 1, "started")
            # Set initial value for lowest distance so we can compare
            lowest_distance: float = 100000
            bottle_num: int
            # Get the drones current position
            async for position in drone.telemetry.position():
                current_location: telemetry.Position = position
                break
            # For each bottle location, get the distance from the drone
            for location in bottle_locations.values():
                distance: float = await self.get_distance(
                    current_location.latitude_deg,
                    current_location.longitude_deg,
                    location["latitude"],
                    location["longitude"],
                )
                if distance < lowest_distance:
                    lowest_distance = distance
                    bottle_loc: dict[str, float] = location
                    bottle_num = [i for i in bottle_locations if bottle_locations[i] == location][0]
            logging.info(
                f'Nearest bottle: #{bottle_num} at ({bottle_loc["latitude"]}, {bottle_loc["longitude"]})'
            )
            # Move to the nearest bottle
            await move_to(drone, bottle_loc["latitude"], bottle_loc["longitude"], 80, 1)
            await airdrop.drop_bottle(bottle_num)
            await asyncio.sleep(
                5
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
