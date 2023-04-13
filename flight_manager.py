"""Controller file to starting flight process"""
import argparse
import logging

from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager

from logger import init_logger, worker_configurer
from communication import Communication
from flight.flight import flight
from flight.states import StateEnum
from flight.state_settings import StateSettings
import time


async def run_time(start: float) -> None:
    """
    Keeps track of run time since this function has been called and if the time is greater than 28 minutes in seconds it calls for the drone to land

    Parameters
    ----------
    start: float
        time in seconds when the drone has started

    Returns
    -------
    None
    """
    # gets the current time and compares it to the time the statemachine was started and returns the difference
    
    now = time.time()
    timespan = now - start
    while(timespan>1680.0):
        time.sleep(60)
        now = time.time()
        timespan = now - start    
    return


class FlightManager:
    """
    Class to initiate state machine and multithreading

    Attributes
    ----------
    state_settings : StateSettings
        Descriptors and parameters for the flight state machine

    Methods
    -------
    main() -> None
        Initiates threads for the flight code
    init_flight(flight_args: tuple[Communication, bool, Queue[str], StateSettings]) -> Process
        Starts a process for the flight state machine
    run_threads(sim: bool) -> None
        Runs the threads for the state machine and ensures machine progresses

    """

    def __init__(self, state_settings: StateSettings) -> None:
        """
        Constructor for the flight manager

        Parameters
        ----------
            state_settings: StateSettings
                Settings for flight state machine
        """
        self.state_settings: StateSettings = state_settings

    def main(self) -> None:
        """
        Central function to run all threads of state machine
        """
        parser: argparse.ArgumentParser = argparse.ArgumentParser()
        parser.add_argument("-s", "--simulation", help="using the simulator", action="store_true")
        args = parser.parse_args()
        logging.debug("Simulation flag %s", "enabled" if args.simulation else "disabled")
        self.run_threads(args.simulation)

    def init_flight(self, flight_args: tuple[Communication, bool, Queue, StateSettings]) -> Process:
        """
        Initializes the flight state machine process

        Parameters
        ----------
        flight_args: Tuple[Communication, bool, Queue, StateSettings]
            Arguments necessary for flight logging and state machine settings
            comm : Communication
                Object to monitor the current state of the machine for flight & vision code
            sim : bool
                Flag to check if simulator is being used
            queue : Queue[str]
                Structure to handle logging messages
            state_settings : StateSettings
                Settings for the flight state machine

        Returns
        -------
        process : Process
            Multiprocessing object for flight state machine
        """
        return Process(target=flight, name="flight", args=flight_args)

    def run_threads(self, sim: bool) -> None:
        """
        Runs the various threads present in the state machine

        Parameters
        ----------
        sim: bool
            Decides if the simulator is active
        """
        # Register Communication object to Base Manager
        BaseManager.register("Communication", Communication)
        # Create manager object
        manager: BaseManager = BaseManager()
        # Start manager
        manager.start()
        # Create Communication object from manager
        comm_obj: Communication = manager.Communication()  # type: ignore[attr-defined]
        log_queue: Queue[str] = Queue(-1)
        logging_process = init_logger(log_queue)
        logging_process.start()

        worker_configurer(log_queue)

        # Create new processes
        logging.info("Spawning Processes")

        flight_args = (comm_obj, sim, log_queue, self.state_settings)
        flight_process: Process = self.init_flight(flight_args)
        # Start flight function
        flight_process.start()
        logging.debug("Flight process with id %d started", flight_process.pid)

        logging.debug(f"Title: {self.state_settings.run_title}")
        logging.debug(f"Description: {self.state_settings.run_description}")

        start = time.time()
        time_process: Process = run_time(start)
        time_process.start()

        try:
            while comm_obj.state != StateEnum.Final_State:
                # State machine is still running
                if flight_process.is_alive() is not True:
                    # Flight process has been killed; restart the process
                    logging.error("Flight process terminated, restarting")
                    flight_process = self.init_flight(flight_args)
                    flight_process.start()
                elif time_process.is_alive() is not True:
                    #time has reached 28 minutes trying to land drone
                    comm_obj.state = StateEnum.Land
                    flight_process = self.init_flight(flight_args)
                    flight_process.start()

        except KeyboardInterrupt:
            # Ctrl-C was pressed
            logging.info("Ctrl-C Pressed, forcing drone to land")
            comm_obj.state = StateEnum.Land
            flight_process = self.init_flight(flight_args)
            flight_process.start()

        # Join flight process before exiting function
        flight_process.join()

        logging.info("All processes ended.")
        logging_process.stop()
