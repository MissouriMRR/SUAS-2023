import asyncio
from multiprocessing import Process
import json

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import ODLC
from state_machine.flight_settings import FlightSettings

async def run_test(_sim: bool) -> None:
    drone = Drone()
    flight_settings = FlightSettings
    await drone.connect_drone()
    await StateMachine(ODLC(drone, flight_settings), drone, flight_settings).run()

    #multiprocessor
    state_machine: Process = Process(
    target=state_machine,
    args=(ODLC(drone, flight_settings), drone, flight_settings),
        )

    #compare test and main data
    with open('flight/data/output.json') as f:
        output_data = json.load(f)
    with open('test.json') as f:
        test_data = json.load(f)
    if output_data == test_data:
        print("Output.json matches test.json")
    else:
        print("Output.json does not match test.json")

if __name__ == "__main__":
    asyncio.run(run_test(True))
