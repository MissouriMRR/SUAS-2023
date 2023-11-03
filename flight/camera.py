"""A class that contains all the needed camera functionality for the drone."""
import socket
import logging
from xml.etree import ElementTree as ET

class Camera:
    def __init__(self) -> None:
        self.address: str = "239.255.255.250:1900"
        self.ssdp_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )
        self.actionURL: str | None = None
        
    async def connect_to_camera(self):
        """Connect to the camera."""
        ssdp_request: str = (
            "M-SEARCH * HTTP/1.1"
            "HOST: 239.255.255.250:1900"
            "MAN: \"ssdp:discover\""
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
            if name == "X_ScalarWebAPI_ActionList_URL": # ActionList_URL item name
                value = item.find("value").text
                logging.info(f"Key: {name}, Value: {value}")
                break
        
        # Close the socket
        self.ssdp_socket.close()
        
        