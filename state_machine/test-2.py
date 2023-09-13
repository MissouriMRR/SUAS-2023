"""Tests the state machine."""

from .drone import Drone
from .state_machine import StateMachine
from .states import Start
import asyncio
from threading import Thread
async def actually_run_drone():
    print("testing")
    drone = Drone()
    await StateMachine(Start(drone), drone).run()

    
def run_drone():
    asyncio.ensure_future(actually_run_drone())
    
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
    
async def test2() -> None:
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
    
