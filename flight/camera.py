"""A class that contains all the needed camera functionality for the drone."""
import json
import socket
import logging
import asyncio
from xml.etree import ElementTree as ET


class Camera:
    def __init__(self) -> None:
        self.address: str = "239.255.255.250:1900"
        self.ssdp_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.actionURL: str | None = None

    async def connect_to_camera(self):
        """Connect to the camera."""
        ssdp_request: str = (
            "M-SEARCH * HTTP/1.1"
            "HOST: 239.255.255.250:1900"
            'MAN: "ssdp:discover"'
            "MX: 1"
            "ST: urn:schemas-sony-com:service:ScalarWebAPI:1"
            "USER-AGENT: SUAS-Drone/1.0"
        )
        self.ssdp_socket.sendto(ssdp_request.encode(), self.address)
        while True:
            data: bytes
            addr: tuple[str, int]
            data, addr = self.ssdp_socket.recvfrom(1024)
            logging.info(f"Received response from {addr}:\n{data.decode()}")
            if "urn:schemas-sony-com:service:ScalarWebAPI:1" in data.decode():
                location: str = data.decode().split("LOCATION: ")[1].split("\r\n")[0]
                logging.info(f"Found actionURL: {self.actionURL}")
                break

        xml_tree = ET.parse(location)
        root = xml_tree.getroot()

        for item in root.findall(".//item"):
            name = item.find("name").text
            if name == "X_ScalarWebAPI_ActionList_URL":  # ActionList_URL item name
                value = item.find("value").text
                logging.info(f"Key: {name}, Value: {value}")
                break

        # Close the socket
        self.ssdp_socket.close()

    async def odlc_move_to(
        drone: System,
        latitude: float,
        longitude: float,
        altitude: float,
        fast_param: float,
        take_photos: float,
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
        take_photos:float
            will take photos with the camera until the position has been reached
        """

        take_photos = True
        info: dict[str, dict[str, int | list[int | float] | float]] = {}

        # get current altitude
        async for terrain_info in drone.telemetry.home():
            absolute_altitude: float = terrain_info.absolute_altitude_m
            break

        await drone.action.goto_location(latitude, longitude, altitude + absolute_altitude, 0)
        location_reached: bool = False
        # First determine if we need to move fast through waypoints or need to slow down at each one
        # Then loops until the waypoint is reached
        while not location_reached:
            logging.info("Going to waypoint")
            async for position in drone.telemetry.position():
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
                name_tuple: tuple = capture_photo()

                point: dict[str, dict[str, int | list[int | float] | float]] = {
                    name_tuple[0]: {
                        "focal_length": 14,
                        "rotation_deg": [
                            drone.offboard.Attitude.roll_deg,
                            drone.offboard.Attitude.pitch_deg,
                            drone.offboard.Attitude.yaw_deg,
                        ],
                        "drone_coordinates": [drone_lat, drone_long],
                        "altitude_f": drone_alt,
                    }
                }

                info.update(point)

                with open("camera.json", "w", encoding="ascii") as camera:
                    json.dump(info, camera)

            # tell machine to sleep to prevent constant polling, preventing battery drain
            await asyncio.sleep(1)
        return
