import asyncio
from mavsdk import System


async def run():
    # Connect to the drone
    drone: System = System()
    await drone.connect(system_address="udp://:14540")

    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Returning to launch...")
        # Use the MAVSDK's `return_to_launch` method to return to launch
        await drone.action.return_to_launch()


try:
    asyncio.run(run())
except KeyboardInterrupt:
    pass
