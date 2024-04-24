"""A unit test for the ODLC state."""

import asyncio
from multiprocessing import Process
import json
import logging
import sys

from state_machine.drone import Drone
from state_machine.state_machine import StateMachine
from state_machine.states import Start
from state_machine.flight_settings import FlightSettings


def start_state_machine(state_machine: StateMachine) -> None:
    """
    Start the state machine.

    Parameters
    ----------
    state_machine: StateMachine
        The state_machine to start
    """
    asyncio.run(state_machine.run())


async def run_test(_sim: bool, odlc_count: int = 5) -> None:
    """
    Tests the the ODLC state in the State Machine. Runs through an example run of the ODLC
    and its functions, testing if the drone can find 5 waypoints, as well as checking to make
    sure the JSON file is output correctly.

    Parameters
    ----------
    _sim: bool
        Whether or not the test is being run in a simulation
    """
    logging.basicConfig(level=logging.INFO)
    drone: Drone = Drone()
    flight_settings: FlightSettings = FlightSettings(sim_flag=_sim, skip_waypoint=True)
    state_machine: StateMachine = StateMachine(
        Start(drone, flight_settings), drone, flight_settings
    )
    state_machine_process: Process = Process(
        target=start_state_machine,
        args=(state_machine,),
    )
    state_machine_process.start()

    activated_odlcs: int = 0
    while activated_odlcs != odlc_count:
        try:
            with open("flight/data/output.json", "r", encoding="UTF-8") as file:
                output_data: str = json.load(file)

            activated_odlcs = len(output_data)

            if activated_odlcs == 5:
                print("All 5 ODLCs were found.")
            else:
                print(f"{activated_odlcs} ODLCs found.")

        except FileNotFoundError:
            print("Output JSON file not found.")
        except json.JSONDecodeError as json_error:
            print(f"Error loading JSON file: {json_error}")

        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run_test("--sim" in sys.argv))
