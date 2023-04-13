"""Initialization Code for Flight State Machine"""
import asyncio
import logging
from mavsdk import System
from mavsdk.core import ConnectionState
import mavsdk
from multiprocessing import Queue

import logger
from communication import Communication
from flight import config
from flight.states import STATES, State, StateEnum
from flight.state_settings import StateSettings
import time

SIM_ADDR: str = "udp://:14540"  # Address to connect to drone simulator
CON_ADDR: str = "serial:///dev/ttyUSB0:921600"  # Address to connect to pixhawk w/ baud rate


class DroneNotFoundError(Exception):
    """
    Exception for when the drone cannot connect
    """

    pass


class StateMachine:
    """
    Class for the flight state machine

    Attributes
    ----------
    current_state : State
        State currently being run in the state machine

    Methods
    -------
    run() -> None
        Initiates the run method for each state in the state machine
    """

    def __init__(self, initial_state: State, drone: System) -> None:
        """
        Initializes flight state machine

        Parameters
        ----------
        initial_state : State
            First state of the flight state machine listed in STATES object
        drone : System
            MAVSDK object for drone control
        """
        self.current_state: State = initial_state
        self.drone: System = drone

    async def run(self) -> None:
        """
        Runs the flight code specific to each state until completion
        """
        while self.current_state:
            self.current_state = await self.current_state.run(self.drone)  # type: ignore[assignment]


async def log_flight_mode(drone: System) -> None:
    """
    Logs the drone's current flight mode

    Parameters
    ----------
    drone : System
        MAVSDK object for drone control
    """
    previous_flight_mode: str = ""
    flight_mode: str
    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode is not previous_flight_mode:
            previous_flight_mode = flight_mode
            logging.debug("Flight Mode: %s", flight_mode)


async def observe_in_air(drone: System, comm: Communication) -> None:
    """
    Monitor if the drone is currently flying, and return when landed

    Parameters
    ----------
    drone : System
        MAVSDK object for drone control
    comm : Communication
        Object to check the current state and enter the final state upon landing
    """
    was_in_air: bool = False
    is_in_air: bool
    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air
        if was_in_air and not is_in_air:
            comm.state = StateEnum.Final_State
            return


async def wait_for_connect(drone: System) -> None:
    """
    Waits for drone to connect before proceeding with flight code

    Parameters
    ----------
    drone : System
        MAVSDK object for drone control
    """
    state: ConnectionState
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.debug("Connected to drone with UUID: %s", state.uuid)
            return


async def init_drone(sim: bool) -> System:
    """
    Initializes flight by connecting to the drone or the simulator

    Parameters
    ----------
    sim : bool
        Flag for if the simulator will be used for current flight

    Returns
    -------
    drone : System
        MAVSDK object for drone control

    Raises
    ------
    DroneNotFoundError
        Will occur if drone fails to connect to simulator/pixhawk in the allotted time
    """
    system_addr: str = SIM_ADDR if sim else CON_ADDR
    drone: System = System()
    await drone.connect(system_addr)
    logging.debug("Waiting for drone to connect...")
    try:
        await asyncio.wait_for(wait_for_connect(drone), timeout=5)
    except asyncio.TimeoutError:
        raise DroneNotFoundError()
    await config.config_params(drone)
    return drone


async def start_flight(comm: Communication, drone: System, state_settings: StateSettings) -> None:
    """
    Creates the flight State Machine and monitors for exceptions

    Parameters
    ----------
    comm : Communication
        Object to facilitate state status information between flight & vision code
    drone : System
        MAVSDK object for drone control
    state_settings : StateSettings
        Basic information & parameters for current flight test
    """
    flight_mode_task = asyncio.ensure_future(log_flight_mode(drone))
    termination_task = asyncio.ensure_future(observe_in_air(drone, comm))
    try:
        initial_state: State = STATES[comm.state](state_settings)
        state_machine: StateMachine = StateMachine(initial_state, drone)
        await state_machine.run()
    except Exception:
        logging.exception("Exception occurred in State Machine")
        try:
            # Stop drone in air
            await drone.offboard.set_position_ned(mavsdk.offboard.PositionNedYaw(0, 0, 0, 0))
            await drone.offboard.set_velocity_ned(mavsdk.offboard.VelocityNedYaw(0, 0, 0, 0))
            await drone.offboard.set_velocity_body(mavsdk.offboard.VelocityBodyYawspeed(0, 0, 0, 0))
            # Have the drone pause
            await asyncio.sleep(config.WAIT)
            try:
                await drone.offboard.stop()
            except mavsdk.offboard.OffboardError as error:
                logging.exception("Stopping offboard mode failed with error code: %s", str(error))
            await asyncio.sleep(config.WAIT)
            logging.info("Landing the drone")
            await drone.action.land()
        except:
            logging.error("No system available")
            comm.state = StateEnum.Final_State
            return
    comm.state = StateEnum.Final_State
    await termination_task
    flight_mode_task.cancel()


async def init_and_begin(comm: Communication, sim: bool, state_settings: StateSettings) -> None:
    """
    Creates the drone object to be passed among state machine

    Parameters
    ----------
    comm : Communication
        Object to relay state information between flight & vision code
    sim : bool
        Sets if the simulator will be used
    state_settings : StateSettings
        Basic information about current flight test
    """
    try:
        drone: System = await init_drone(sim)
        await start_flight(comm, drone, state_settings)
    except DroneNotFoundError:
        logging.exception("Drone not found")
        return
    except:
        logging.exception("Uncaught error")
        return


def flight(
    comm: Communication, sim: bool, log_queue: Queue[str], state_settings: StateSettings
) -> None:
    """
    Starts asynchronous event loop for flight code

    Parameters
    ----------
    comm : Communication
        Object for state communication between flight & vision code
    sim : bool
        Sets if the simulator is being used for current flight
    log_queue : Queue
        Structure of logging processes to handle
    state_settings : StateSettings
        Basic information about current flight passed between states in State Machine
    """
    logger.worker_configurer(log_queue)
    logging.debug("Flight process started")
    asyncio.run(init_and_begin(comm, sim, state_settings))

def run_time(start: float) -> None:
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
    start = time.time()
    now = time.time()
    timespan = now - start
    while(timespan>1680.0):
        time.sleep(60)
        now = time.time()
        timespan = now - start    
    return