"""A class that contains all the needed camera functionality for the drone."""

import asyncio
import json
import logging
import os
from datetime import datetime

import gphoto2

from state_machine.drone import Drone


class Camera:
    """
    Initialize a new Camera object to control the Sony RX100-VII camera on the drone

    Attributes
    ----------
    camera : gphoto2.Camera
        The gphoto2 camera object.
    session_id : int
        The session id for the current session.
        This will start at 0 the first time pictures are taken on a given day.
        Will then increment by 1 for each session on a given day.
    image_id : int
        The image id for the current image.
        Starts at 0 and increments by 1 for each image taken.

    Methods
    -------
    capture_photo(path: str = f"{os.getcwd()}/images/")
        Capture a photo and save it to the specified path.
        The default path is the images folder in the current working directory.
        The file name will be the file format attribute.
        Returns the file name and the file path.
    odlc_move_to(
        drone: Drone,
        latitude: float,
        longitude: float,
        altitude: float,
        fast_param: float,
        take_photos: float
    )
        Move the drone to the specified latitude, longitude, and altitude.
        Takes photos along the way if take_photos is True.
    """

    def __init__(self) -> None:
        self.camera: gphoto2.Camera = gphoto2.Camera()
        self.camera.init()

        self.session_id: int = 0
        if os.path.exists(f"{os.getcwd()}/images/"):
            for file in os.listdir(f"{os.getcwd()}/images/"):
                if file.startswith(f"{datetime.now().strftime('%Y%m%d')}"):
                    if int(file.split("_")[1]) >= self.session_id:
                        self.session_id = int(file.split("_")[1]) + 1

        self.image_id: int = 0

        logging.info("Camera initialized")

    async def capture_photo(self, path: str = f"{os.getcwd()}/images/") -> tuple[str, str]:
        """
        Capture a photo and save it to the specified path.

        Parameters
        ----------
        path : str, optional
            The path to save the image to, by default f"{os.getcwd()}/images/"


        Returns
        -------
        tuple[str, str]
            The file name and the file path.
        """
        # If the images folder doesn't exist, we can't save images.
        # So we have to make sure the images folder exists.
        os.makedirs(path, mode=0o777, exist_ok=True)

        file_path = self.camera.capture(gphoto2.GP_CAPTURE_IMAGE)
        while True:
            event_type, _event_data = self.camera.wait_for_event(100)
            if event_type == gphoto2.GP_EVENT_CAPTURE_COMPLETE:
                photo_name: str = (
                    f"{datetime.now().strftime('%Y%m%d')}_{self.session_id}_{self.image_id:04d}.jpg"
                )

                cam_file = gphoto2.check_result(
                    gphoto2.gp_camera_file_get(
                        self.camera,
                        file_path.folder,
                        file_path.name,
                        gphoto2.GP_FILE_TYPE_NORMAL,
                    )
                )
                target_name: str = f"{path}{photo_name}"
                cam_file.save(target_name)
                self.image_id += 1
                logging.info("Image is being saved to %s", target_name)
                return target_name, photo_name

    async def odlc_move_to(
        self,
        drone: Drone,
        latitude: float,
        longitude: float,
        altitude: float,
        fast_param: float,
        take_photos: bool,
    ) -> None:
        """
        This function takes in a latitude, longitude and altitude and autonomously
        moves the drone to that waypoint. This function will also auto convert the altitude
        from feet to meters. It will take photos along the path if passed true in take_photos and
        add the point and name of photo to a json

        Parameters
        ----------
        drone: System
            a drone object that has all offboard data needed for computation
        latitude: float
            a float containing the requested latitude to move to
        longitude: float
            a float containing the requested longitude to move to
        altitude: float
            a float contatining the requested altitude to go to in meters
        fast_param: float
            a float that determines if the drone will take less time checking its precise location
            before moving on to another waypoint. If its 1, it will move at normal speed,
            if its less than 1(0.83), it will be faster.
        take_photos: bool
            will take photos with the camera until the position has been reached
        """
        if take_photos:
            await drone.system.action.set_maximum_speed(5)

        info: dict[str, dict[str, int | list[int | float] | float]] = {}

        # get current altitude
        async for terrain_info in drone.system.telemetry.home():
            absolute_altitude: float = terrain_info.absolute_altitude_m
            break

        await drone.system.action.goto_location(
            latitude, longitude, altitude + absolute_altitude, 0
        )
        location_reached: bool = False
        # First determine if we need to move fast through waypoints or need to slow down at each one
        # Then loops until the waypoint is reached
        while not location_reached:
            logging.info("Going to waypoint")
            async for position in drone.system.telemetry.position():
                # continuously checks current latitude, longitude and altitude of the drone
                drone_lat: float = position.latitude_deg
                drone_long: float = position.longitude_deg
                drone_alt: float = position.relative_altitude_m

                #  accurately checks if location is reached and stops for 15 secs and then moves on.
                if (
                    (round(drone_lat, int(6 * fast_param)) == round(latitude, int(6 * fast_param)))
                    and (
                        round(drone_long, int(6 * fast_param))
                        == round(longitude, int(6 * fast_param))
                    )
                    and (round(drone_alt, 1) == round(altitude, 1))
                ):
                    location_reached = True
                    logging.info("arrived")
                    break

            if take_photos:
                _full_path: str
                file_path: str
                _full_path, file_path = await self.capture_photo()

                point: dict[str, dict[str, int | list[int | float] | float]] = {
                    file_path: {
                        "focal_length": 14,
                        "rotation_deg": [
                            drone.system.offboard.Attitude.roll_deg,
                            drone.system.offboard.Attitude.pitch_deg,
                            drone.system.offboard.Attitude.yaw_deg,
                        ],
                        "drone_coordinates": [drone_lat, drone_long],
                        "altitude_f": drone_alt,
                    }
                }

                info.update(point)

                with open("camera.json", "w", encoding="ascii") as camera:
                    json.dump(info, camera)

            if take_photos:
                await drone.system.action.set_maximum_speed(20)
            # tell machine to sleep to prevent constant polling, preventing battery drain
            await asyncio.sleep(1)
        return
