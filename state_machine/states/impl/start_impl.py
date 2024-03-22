"""Implements the behavior of the Start state."""

import asyncio
import logging

from state_machine.state_tracker import update_state

from state_machine.states.start import Start
from state_machine.states.state import State
from state_machine.states.takeoff import Takeoff


async def run(self: Start) -> State:
    """
    Implements the run method for the Start state.

    This method establishes a connection with the drone, waits for the drone to be
    discovered, ensures the drone has a global position estimate, arms the drone,
    and transitions to the Takeoff state.

    Returns
    -------
    Takeoff : State
        The next state after the Start state has successfully run.

    Notes
    -----
    This method is responsible for initializing the drone and transitioning it to the
    Takeoff state, which is the next step in the state machine.

    """
    try:
        update_state("Start")
        logging.info("Start state running")
        await self.drone.connect_drone()

        # connect to the drone
        logging.info("Waiting for drone to connect...")
        async for state in self.drone.system.core.connection_state():
            if state.is_connected:
                logging.info("Drone discovered!")
                break

        logging.info("Waiting for drone to have a global position estimate...")
        async for health in self.drone.system.telemetry.health():
            if health.is_global_position_ok:
                logging.info("Global position estimate ok")
                break

        logging.info("-- Arming")
        await self.drone.system.action.arm()

        logging.info("Start state complete")
        return Takeoff(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("Start state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the Start class to the run function
Start.run_callable = run
