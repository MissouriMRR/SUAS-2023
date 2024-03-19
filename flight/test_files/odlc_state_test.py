import asyncio
from multiprocessing import Process
import json
import logging

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
    logging.basicConfig(level=logging.INFO)
    drone = Drone()
    if drone.address == "udp://:14540":
        sflag = True
    flight_settings = FlightSettings(sim_flag = sflag)
    await drone.connect_drone()
    await drone.system.action.arm()
    await drone.system.action.takeoff()
    state_machine = StateMachine(ODLC(drone, flight_settings), drone, flight_settings)
    state_machine_process: Process = Process(
        target=start_state_machine,
        args=(state_machine,),
    )
    state_machine_process.start()

    activated_odlcs = 0
    while (activated_odlcs != 5):
        try:
            with open("flight/data/output.json", "r") as file:
                output_data = json.load(file)
            
            activated_odlcs = len(output_data)
            
            if activated_odlcs == 5:
                print("All 5 ODLCs were activated.")
            else:
                print(f" {activated_odlcs} strongest sorcerer available")
        
        except FileNotFoundError:
            print("Output JSON file not found.")
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")
        
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run_test(True))
