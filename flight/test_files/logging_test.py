"""Runs the state machine and logging in seperate process to test them"""
import logging
import asyncio
import multiprocessing

from logging import handlers

from listener import listener_process

from state_machine.flight_manager import FlightManager

SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board

logger = logging.getLogger("__main__")  # use module name


def root_configurer(queue) -> None:  # type: ignore
    """
    Configures root for logging

    Parameters
    ----------
    queue : Queue
        The queue from multiprocessing
    """
    handler = handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


async def run_test(sim: bool) -> None:
    """
    Run the state machine.

    Parameters
    ----------
    sim : bool
        Whether to run the state machine in simulation mode.
    """
    queue = multiprocessing.Queue(-1)  # type: ignore
    listener = multiprocessing.Process(target=listener_process, args=(queue,))
    listener.start()

    root_configurer(queue)

    logger.info("Logging from main")
    FlightManager().start_manager(sim)
    logger.info("main function ends")


if __name__ == "__main__":
    asyncio.run(run_test(True))
