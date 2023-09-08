"""Tests the state machine."""

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


async def test() -> None:
    """Test the state machine."""
    drone = Drone()
    await StateMachine(Start(drone), drone).run()
