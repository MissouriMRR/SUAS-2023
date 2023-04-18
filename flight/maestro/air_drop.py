"""
File containing a class to control air drop functions
"""

from flight.maestro.maestro import Maestro


class AirdropControl:
    """
    Class to control the air drop functions

    Attributes
    ----------
    board: Maestro
        The Maestro board object to control the servos

    Methods
    -------
    drop_bottle(bottle: int) -> None
        Drops the bottle from the drone
    close_servo(bottle: int) -> None
        Closes the servo after bottle has been dropped
    """

    def __init__(self, connection_address: str = "/dev/ttyACM0", device_number: int = 12) -> None:
        """
        Initializes the Maestro board object

        Parameters
        ----------
        connection_address: str = '/dev/ttyACM0'
            The command serial port of the Maestro board (usually '/dev/ttyACM0')
        device_number: int = 12
            The device number of the Maestro board
        """
        self.board = Maestro(connection_address, device_number)

    def drop_bottle(self, bottle: int) -> None:
        """
        Drops the bottle from the drone

        Parameters
        ----------
        bottle : int
            The number of the bottle to be dropped
        """
        # I'm going to assume that we want to open the bottle by setting the servo full right
        self.board.set_target(bottle, 8000)

    def close_servo(self, bottle: int) -> None:
        """
        Closes the servo after bottle has been dropped

        Parameters
        ----------
        bottle : int
            The number of the bottle to be closed
        """
        self.board.set_target(bottle, 4000)
