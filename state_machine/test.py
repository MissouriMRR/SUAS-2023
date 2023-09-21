"""Tests the state machine."""

import asyncio
from multiprocessing import Process
import time

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


def run_new_state_machine() -> None:
    """Creat and run a state machine. This function is synchronous."""
    drone: Drone = Drone()
    state_machine = StateMachine(Start(drone), drone)
    asyncio.new_event_loop().run_until_complete(state_machine.run())


def test(cancel_delay: float = 1e9) -> None:
    """Test the state machine.

    Parameters
    ----------
    cancel_delay : float
        The number of seconds to cancel the state machine after
    """
    print(f"The state machine will be canceled after {cancel_delay} seconds.")

    state_machine_process: Process = Process(
        target=run_new_state_machine, name="Multirotor State Machine"
    )

    state_machine_process.start()
    time.sleep(cancel_delay)
    state_machine_process.terminate()
    print("State machine terminated")
