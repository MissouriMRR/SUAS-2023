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

    def init_flight(
        self, flight_args: tuple[Communication, bool, Queue[str], StateSettings]
    ) -> Process:
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

        logging.debug("Title: %s", self.state_settings.run_title)
        logging.debug("Description: %s", self.state_settings.run_description)

        time_process: Process = Process(target=flight, name="run_time")
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
                    # time has reached 28 minutes trying to land drone
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
