"""Implements the behavior of the ODLC state."""

import asyncio
from ctypes import c_bool
from multiprocessing import Process, Value
from multiprocessing.sharedctypes import SynchronizedBase
import logging
import json

from flight.camera import Camera
from state_machine.state_tracker import update_state
from state_machine.states.airdrop import Airdrop
from state_machine.states.odlc import ODLC
from state_machine.states.state import State
from vision.flyover_vision_pipeline import flyover_pipeline


async def run(self: ODLC) -> State:
    """
    Implements the run method for the ODLC state.

    This method initiates the ODLC scanning process of the drone, takes pictures and transfers
    picture data to the vision code, and then transitions to the Airdrop state.

    Parameters
    ----------
    self : ODLC
        The current instance of the ODLC state.

    Returns
    -------
    Airdrop : State
        The next state after the drone has successfully scanned the ODLC area.

    Raises
    ------
    asyncio.CancelledError
        If the execution of the ODLC state is canceled.

    Notes
    -----
    The type hinting for the capture_status variable is broken, see
    https://github.com/python/typeshed/issues/8799
    """
    try:
        update_state("ODLC")
        # Syncronized type hint is broken, see https://github.com/python/typeshed/issues/8799
        capture_status: SynchronizedBase[c_bool] = Value(c_bool, False)  # type: ignore

        flight_process = Process(
            target=flight_odlc_logic,
            args=(
                self,
                capture_status,
            ),
        )
        vision_process = Process(target=vision_odlc_logic, args=(capture_status,))

        flight_process.start()
        vision_process.start()
        try:
            flight_process.join()
            logging.info("Flight process joined")
            vision_process.join()
            logging.info("Vision process joined")

            logging.info("Done!")
        except KeyboardInterrupt:
            logging.critical(
                "Keyboard interrupt detected. Killing state machine and landing drone."
            )
        return Airdrop(self.drone, self.flight_settings)
    except asyncio.CancelledError as ex:
        logging.error("ODLC state canceled")
        raise ex
    finally:
        pass


def flight_odlc_logic(self: ODLC, capture_status: "SynchronizedBase[c_bool]") -> None:
    """
    Starts the asyncronous flight logic for the ODLC state.

    Parameters
    ----------
    self : ODLC
        The current instance of the ODLC state.
    capture_status : SynchronizedBase[c_bool]
        If pictures are done being taken or not.
    """
    asyncio.run(find_odlcs(self, capture_status))


async def find_odlcs(self: ODLC, capture_status: "SynchronizedBase[c_bool]") -> None:
    """
    Implements the run method for the ODLC state.

    Returns
    -------
    Airdrop : State
        The next state after the drone has successfully scanned the ODLC area.

    Notes
    -----
    This method is responsible for initiating the ODLC scanning process of the drone
    and transitioning it to the Airdrop state.
    """
    try:
        logging.info("ODLC")

        # Initialize the camera
        camera: Camera = Camera()

        # These waypoint values are all that are needed to traverse the whole odlc drop location
        # because it is a small rectangle
        # The first waypoint is the midpoint of
        # the left side of the rectangle(one of the short sides), the second point is the
        # midpoint of the right side of the rectangle(other short side),
        # and the third point is the top left corner of the rectangle
        # it goes there for knowing where the drone ends to travel to each of the drop locations,
        # the altitude is locked at 100 because
        # we want the drone to stay level and the camera to view the whole odlc boundary
        # the altitude 100 feet was chosen to cover the whole odlc boundary
        # because the boundary is 70ft by 360ft the fov of the camera
        # is vertical 52.1 degrees and horizontal 72.5,
        # so using the minimum length side of the photo the coverage would be 90 feet allowing
        # 10 feet overlap on both sides
        waypoint: dict[str, list[float]] = {
            "lats": [38.31451966813249, 38.31430872867596, 38.31461622313521],
            "longs": [-76.54519982319357, -76.54397320409971, -76.54516993186949],
            "Altitude": [100],
        }

        # traverses the 3 waypoints starting at the midpoint on left to midpoint on the right
        # then to the top left corner at the rectangle
        with open("flight/data/output.json", encoding="ascii") as output:
            airdrop_dict = json.load(output)
            airdrops: int = len(airdrop_dict)
            point: int
        while airdrops != 5:
            logging.info("Starting odlc zone flyover")

            for point in range(3):
                take_photos: bool = False

                if point == 0:
                    logging.info("Moving to the center of the west boundary")
                elif point == 1:
                    # starts taking photos at a .5 second interval because we want
                    # to get multiple photos of the boundary so there is overlap and
                    # the speed of the drone should be 20 m/s which is 64 feet/s which means
                    # it will traverse the length of the boundary (360 ft) in 6 sec
                    # and that means with the shortest length of photos
                    #  being taken depending on rotation
                    # would be 90 feet and we want to take multiple photos
                    # so we would need a minimum of 4 photos to cover
                    #  the whole boundary and we want multiple,
                    # so using .5 seconds between each photo allows
                    # it to take a minimum of 12 photos of
                    #  the odlc boundary which will capture the whole area

                    logging.info("Moving to the center of the east boundary")
                    take_photos = True

                elif point == 2:
                    capture_status.value = c_bool(True)  # type: ignore
                    logging.info("Moving to the north west corner")

                await camera.odlc_move_to(
                    self.drone,
                    waypoint["lats"][point],
                    waypoint["longs"][point],
                    waypoint["Altitude"][0],
                    5 / 6,
                    take_photos,
                )

            with open("flight/data/output.json", encoding="ascii") as output:
                airdrop_dict = json.load(output)
                airdrops = len(airdrop_dict)

        self.drone.odlc_scan = False
    except asyncio.CancelledError as ex:
        logging.error("ODLC state canceled")
        raise ex
    finally:
        pass


def vision_odlc_logic(capture_status: "SynchronizedBase[c_bool]") -> None:
    """
    Implements the run method for the ODLC state.

    Returns
    -------
    Airdrop : State
        The next state after the drone has successfully scanned the ODLC area.

    Notes
    -----
    This method is responsible for initiating the ODLC scanning process of the drone
    and transitioning it to the Airdrop state.
    """
    try:
        flyover_pipeline("flight/data/camera.json", capture_status, "flight/data/output.json")
    except asyncio.CancelledError as ex:
        logging.error("ODLC state canceled")
        raise ex
    finally:
        pass


# Setting the run_callable attribute of the ODLC class to the run function
ODLC.run_callable = run
