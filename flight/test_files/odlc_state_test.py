"""
code to test if odlc state functions correctly
"""

import asyncio
from multiprocessing import Process
import json

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import ODLC
from state_machine.flight_settings import FlightSettings


async def run_test(_sim: bool) -> None:
    """
    add
    """

    drone = Drone()
    flight_settings = FlightSettings()
    await drone.connect_drone()
    await StateMachine(ODLC(drone, flight_settings), drone, flight_settings).run()

    state_machine: Process = Process(
        target=StateMachine,
        args=(ODLC(drone, flight_settings), drone, flight_settings),
    )
    state_machine.start()

    # compare test and main data
    with open("flight/data/output.json") as file:
        output_data = json.load(file)
    with open("test.json") as file:
        test_data = json.load(file)
    if output_data == test_data:
        print("Output.json matches test.json")
    else:
        print("Output.json does not match test.json")


if __name__ == "__main__":
    asyncio.run(run_test(True))
