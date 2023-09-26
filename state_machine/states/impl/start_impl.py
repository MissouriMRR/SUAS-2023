"""Implements the run_callable class attribute of the Start class."""

import asyncio
import logging

from ..start import Start
from ..state import State
from ..takeoff import Takeoff


async def run(self: Start) -> State:
    """Implements the run method."""
    try:
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
        return Takeoff(self.drone)
    except asyncio.CancelledError as ex:
        print("Start state canceled")
        raise ex
    finally:
        pass


Start.run_callable = run
