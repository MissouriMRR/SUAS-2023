import asyncio
from multiprocessing import Process
import json

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import ODLC
from state_machine.flight_settings import FlightSettings

def start_state_machine(state_machine: StateMachine) -> None:
        """
        add
        """
        asyncio.run(state_machine.run())

async def run_test(_sim: bool) -> None:
    """
    add
    """
    drone = Drone()
    flight_settings = FlightSettings()
    await drone.connect_drone()
    state_machine = StateMachine(ODLC(drone, flight_settings), drone, flight_settings)
    state_machine_process: Process = Process(
        target=start_state_machine,
        args=(state_machine,),
    )
    state_machine_process.start()

    # compare test and main data
    try:
        with open("flight/data/output.json") as file:
            output_data = json.load(file)
        with open("flight/data/test.json") as file:
            test_data = json.load(file)
        if output_data == test_data:
            print("Output.json matches test.json")
        else:
            print("Output.json does not match test.json")
    except json.JSONDecodeError as e:
        print(f"Error loading JSON file: {e}")


if __name__ == "__main__":
    asyncio.run(run_test(True))
