"""
Test code for our drone in obstacle avoidance
"""

import asyncio

import mavsdk.core
import mavsdk.telemetry


async def run() -> None:
    """
    Runs test code
    """

    drone: mavsdk.System = mavsdk.System()
    print("Will connect")
    await drone.connect(system_address="udp://:14540")
    print("Connected")

    status_text_task: asyncio.Task[None] = asyncio.ensure_future(print_status_text(drone))

    print("Waiting for drone to connect...")
    state: mavsdk.core.ConnectionState
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    health: mavsdk.telemetry.Health
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    await drone.action.takeoff()

    await asyncio.sleep(10)

    print("-- Landing")
    await drone.action.land()

    status_text_task.cancel()


async def print_status_text(drone: mavsdk.System) -> None:
    """
    Prints status text
    """

    try:
        status_text: mavsdk.telemetry.RcStatus
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


if __name__ == "__main__":
    loop: asyncio.AbstractEventLoop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(run())
