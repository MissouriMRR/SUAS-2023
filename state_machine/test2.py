"""Tests the state machine."""

import asyncio
from multiprocessing import Process
import time

from .drone import Drone
from .state_machine import StateMachine
from .states import Start


async def actually_run_drone(drone: Drone) -> None:
    """Create and run a state machine machine for the drone."""
    print("testing")
    await StateMachine(Start(drone), drone).run()


def run_drone(drone: Drone) -> None:
    """Create and run a state machine in the event loop."""
    print("Running drone")
    asyncio.run(actually_run_drone(drone))


def process_test() -> None:
    """Test running the state machine in a separate process."""
    drone_obj: Drone = Drone()

    print("Starting processes")
    state_machine: Process = Process(target=run_drone, args=(drone_obj,))
    kill_switch_process: Process = Process(target=kill_switch, args=(state_machine,))

    state_machine.start()
    kill_switch_process.start()

    state_machine.join()
    print("State machine joined")
    kill_switch_process.join()
    print("Kill switch joined")

    print("Done!")


def kill_switch(state_machine_process: Process) -> None:
    """Kill the state machine after approximately 20 seconds"""
    for i in range(20):
        print(f"Kill switch is on cycle {i}")
        time.sleep(1)
    state_machine_process.terminate()
