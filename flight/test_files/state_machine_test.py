"""File that runs the state machine and kill switch in separate processes in order to test them."""
import asyncio
from state_machine.flight_manager import FlightManager

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board


async def run_test(_sim: bool) -> None:  # Temporary fix for unused variable
    """Runs the state machine.

    Args:
        _sim (bool): Whether or not to run the state machine in simulation mode.
    """
    FlightManager().start_manager()


if __name__ == "__main__":
    # sim = input("Simulate? (y/n): ").lower() == "y"
    asyncio.run(run_test(True))
