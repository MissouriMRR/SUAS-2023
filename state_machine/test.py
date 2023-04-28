from state_machine.state_machine import StateMachine
from state_machine.drone import Drone
from state_machine.states.start import Start
import asyncio

async def run():

    drone = Drone()
    state_machine = StateMachine(Start, drone)
    await state_machine.run()