"""Tests the state machine."""

import asyncio

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


async def test(cancel_delay: float = 1e9) -> None:
    """Test the state machine.

    Parameters
    ----------
    cancel_delay : float
        The number of seconds to cancel the state machine after
    """
    print(f"The state machine will be canceled after {cancel_delay} seconds.")

    drone = Drone()
    state_machine = StateMachine(Start(drone), drone)
    asyncio.ensure_future(state_machine.run())

    await asyncio.sleep(cancel_delay)
    state_machine.cancel()
    await asyncio.sleep(1.0)
