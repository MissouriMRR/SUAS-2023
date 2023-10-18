import asyncio
from mavsdk import System
from flight.states.state import State
from flight.state_settings import StateSettings
from flight_manager import FlightManager

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board


async def run_test(sim: bool) -> None:
    FlightManager(StateSettings).run_threads(sim)


if __name__ == "__main__":
    sim = input("Simulate? (y/n): ").lower() == "y"
    asyncio.run(run_test(sim))
