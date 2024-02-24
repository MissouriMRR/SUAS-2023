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
flight_settings = FlightSettings

async def run_test(_sim: bool) -> None:  # Temporary fix for unused variable
    await drone.connect_drone()
    await StateMachine(ODLC(drone, flight_settings), drone, flight_settings).run()
    #check locations and objects after?
    
    state_machine: Process = Process(
    target=state_machine,
    args=(ODLC(drone, flight_settings), drone, flight_settings),
        )
    
    f = open('flight/data/output.json')
    data = json.load(f)
    for i in data['emp_details']:
        print(i)
    f.close()

    #flight manager line 57 starts process at same time

if __name__ == "__main__":
    asyncio.run(run_test(True))
