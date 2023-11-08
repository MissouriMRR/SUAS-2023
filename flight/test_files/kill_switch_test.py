import asyncio
import threading
import random
from mavsdk.manual_control import ManualControl
import logging
import sys
sys.path.append('/home/james/SUAS-2023')

from state_machine.flight_manager import FlightManager
from state_machine.drone import Drone

CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board
# Test set of manual inputs. Format: [roll, pitch, throttle, yaw]
manual_inputs = [
    [0, 0, 0.5, 0],  # no movement
    [-1, 0, 0.5, 0],  # minimum roll
    [1, 0, 0.5, 0],  # maximum roll
    [0, -1, 0.5, 0],  # minimum pitch
    [0, 1, 0.5, 0],  # maximum pitch
    [0, 0, 0.5, -1],  # minimum yaw
    [0, 0, 0.5, 1],  # maximum yaw
    [0, 0, 1, 0],  # max throttle
    [0, 0, 0, 0],  # minimum throttle
]


async def manual_controls(drone: Drone):
    """Main function to connect to the drone and input manual controls"""
    # Connect to the Simulation
    await drone.system.connect(system_address="udp://:14540")

    # This waits till a mavlink based drone is connected
    print("Waiting for drone to connect...")
    async for state in drone.system.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    # Checking if Global Position Estimate is ok
    async for health in drone.system.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break

    # set the manual control input after arming
    await drone.system.manual_control.set_manual_control_input(
        float(0), float(0), float(0.5), float(0)
    )

    # Arming the drone
    print("-- Arming")
    await drone.system.action.arm()

    # Takeoff the vehicle
    print("-- Taking off")
    await drone.system.action.takeoff()
    await asyncio.sleep(5)

    # set the manual control input after arming
    await drone.system.manual_control.set_manual_control_input(
        float(0), float(0), float(0.5), float(0)
    )

    # start manual control
    print("-- Starting manual control")
    await drone.system.manual_control.start_position_control()

    while True:
        # grabs a random input from the test list
        # WARNING - your simulation vehicle may crash if its unlucky enough
        input_index = random.randint(0, len(manual_inputs) - 1)
        input_list = manual_inputs[input_index]

        # get current state of roll axis (between -1 and 1)
        roll = float(input_list[0])
        # get current state of pitch axis (between -1 and 1)
        pitch = float(input_list[1])
        # get current state of throttle axis
        # (between -1 and 1, but between 0 and 1 is expected)
        throttle = float(input_list[2])
        # get current state of yaw axis (between -1 and 1)
        yaw = float(input_list[3])

        await drone.system.manual_control.set_manual_control_input(
            pitch, roll, throttle, yaw)

        await asyncio.sleep(0.1)

def run_manager(manager: FlightManager):
    manager.start_manager()

async def activate_manual_mode(drone: Drone):
    try:
        # Make sure the drone is connected
        await drone.connect_drone()
        async for state in drone.system.core.connection_state():
            if state.is_connected:
                break
            else:
                print("Waiting for connection...")
                await asyncio.sleep(1)

        # Set the initial manual control input
        await drone.system.manual_control.set_manual_control_input(
            float(0), float(0), float(0.5), float(0)
        )

        # Start position control in manual mode
        print("-- Starting manual control")
        await drone.system.manual_control.start_position_control()
    
    except Exception as e:
        print(f"Failed to switch to manual mode: {e}")
        
async def run_test(_sim: bool) -> None:
    manager = FlightManager()  # Assuming FlightManager is now designed to be async
    
    # Start the manager with only one argument
    manager_thread = threading.Thread(target=run_manager, args=(manager,))
    manager_thread.start()

    await asyncio.sleep(50)  # Give some time to initialize

    await manual_controls(manager.drone_obj)  # Activate manual mode

    # Your kill switch should get activated when the drone enters manual mode

    manager_thread.join()  # Wait for manager_thread to complete

    await asyncio.sleep(3600) 
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_test(True))
