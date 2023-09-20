"""Tests the state machine."""

from .drone import Drone
from .state_machine import StateMachine
from .states import Start
import asyncio
from threading import Thread
import multiprocessing
import time
async def actually_run_drone(drone: Drone):
    print("testing")
    await StateMachine(Start(drone), drone).run()

    
def run_drone(drone: Drone):
    print("Running drone")
    asyncio.run(actually_run_drone(drone))
    
async def stop_states():
    print("Stopping states")
    await asyncio.sleep(1)
    print("stopping now")
    current_loop = asyncio.get_running_loop()
    tasks = asyncio.all_tasks(current_loop)
    for task in tasks:
        print(task)
        status = task.cancel()
        print(status)
    
async def threat_test() -> None:
    """Test the state machine."""

    t = Thread(target=run_drone)

    t.run()
    
    await asyncio.sleep(5)
    print("stop it now!!")
    # Create a coroutine
    loop = asyncio.get_running_loop()
    
    print("1")
    # Submit the coroutine to a given loop
    asyncio.run_coroutine_threadsafe(stop_states(), loop)
    print("2")
    
    while True:
        await asyncio.sleep(5)
    # Wait for the result with an optional timeout argument
    #assert future.result(timeout=6run_drone)
    
def process_test():
    drone_obj = Drone()
    
    print("Starting processes")
    state_machine = multiprocessing.Process(target=run_drone, args=(drone_obj, ))
    kill_switch_process = multiprocessing.Process(target=kill_switch, args=(state_machine, ))
    
    state_machine.start()
    kill_switch_process.start()
    
    state_machine.join()
    print("State machine joined")
    kill_switch_process.join()
    print("Kill switch joined")
    
    print("Done!")
    
    
def kill_switch(state_machine_process: multiprocessing.Process):
    i = 0
    while (i < 20):
        print(f"Kill switch is on cycle {i}")
        time.sleep(1)
        i += 1
    state_machine_process.terminate()