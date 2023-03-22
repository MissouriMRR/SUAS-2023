"""
File containing the Maestro class to be able to control the Maestro board
"""

import time
import serial


class Maestro:
    """
    Maestro class to control the Maestro board

    Attributes
    ----------
    serial: serial.Serial
        Serial object to be able to read and send messages to and from the board.
    command_prefix: str
        The command protocol prefix that is sent before every command to the board.
    targets: list[int]
        A list of the current targets for each channel.

    Methods
    -------
    _send_command(command: str) -> None
        Sends a serial command to the board
    _get_bits(integer: int) -> tuple[int, int]
        Converts an integer value to the 7 high bit, 7 low bit format that the Pololu commands use
    _read_bits() -> int
        Read a 16 bit response from the Maestro board and convert it to an integer
    set_target(channel: int, target: int) -> None
        Sets the target position of the specified servo
    set_speed(channel: int, speed: int) -> None
        Sets the speed limit of the desired servo
    set_acceleration(channel: int, accel: int) -> None
        Sets the target position of the specified servo
    get_position(channel: int) -> int
        Returns the current position of the servo
    get_moving_state() -> bool
        States if any servos are currently moving
    getError() -> bool
        States if there is an error with the board
    go_home() -> None
        Sets all servos to their home position
    is_moving() -> bool
        Checks if a certain servo is still moving
    """

    def __init__(
        self,
        connection_address: str = "/dev/ttyACM0",
        device_number: int = 12,
        baud_rate: int = 9600,
    ):
        """
        Initializes a serial object to connect to the Maestro board

        Parameters
        ----------
        connection_address: str = '/dev/ttyACM0'
            The command serial port of the Maestro board (usually '/dev/ttyACM0')
        device_number: int = 12
            The device number that is used to address the board in Pololu Protocol commands
        baud_rate: int = 9600
            The rate of communication configured for the board (default 9600)
        """
        self.serial: serial.Serial = serial.Serial(
            port=connection_address, baudrate=baud_rate, timeout=0.050
        )
        self.command_prefix: str = chr(0xAA) + chr(device_number)
        self.targets: list[int] = [-1] * 24

    def _send_command(self, command: str) -> None:
        """
        Sends a serial command to the board

        Parameters
        ----------
        command: str
            The command (in bits) to be sent to the board
        """
        self.serial.write(bytes(self.command_prefix + command, "latin-1"))

    def _get_bits(self, integer: int) -> tuple[int, int]:
        """
        Converts an integer value to the 7 high bit, 7 low bit format that the Pololu commands use

        Parameters
        ----------
        integer: int
            The number to be converted to bits

        Returns
        -------
        bits: tuple[int, int]
            low_bits: int
                The 7 low bits of the integer
            high_bits: int
                The 7 high bits of the integer

        Notes
        -----
        See the Pololu Protocol documentation here: https://www.pololu.com/docs/0J40/5.e
        """
        low_bits: int = integer & 0x7F
        high_bits: int = (integer >> 7) & 0x7F
        return low_bits, high_bits

    def _read_bits(self) -> int:
        """
        Read a 16 bit response from the Maestro board and convert it to an integer

        Returns
        -------
        result: int
            The response from the board
        """
        lsb: int = ord(self.serial.read())
        msb: int = ord(self.serial.read())
        return (msb << 8) + lsb

    def set_target(self, channel: int, target: int) -> None:
        """
        Sets the target position of the specified servo

        Parameters
        ----------
        channel: int
            The channel of the desired servo
        target: int
            The target position in units of quarter-microseconds

        Notes
        -----
        To set the servos on the drone to full left, set the target to 4000.
        To set the servos to full right, set the target to 8000.
        The range of the servo target is 4000 - 8000.
        """
        low: int
        high: int
        low, high = self._get_bits(target)
        command: str = chr(0x04) + chr(channel) + chr(low) + chr(high)

        self._send_command(command)
        self.targets[channel] = target

    def set_speed(self, channel: int, speed: int) -> None:
        """
        Sets the speed limit of the desired servo

        Parameters
        ----------
        channel: int
            The channel of the desired servo
        speed: int
            The speed limit to set the channel to in units of quarter-microseconds/10 ms
        """
        low: int
        high: int
        low, high = self._get_bits(speed)

        command: str = chr(0x07) + chr(channel) + chr(low) + chr(high)
        self._send_command(command)

    def set_acceleration(self, channel: int, accel: int) -> None:
        """
        Sets the target position of the specified servo

        Parameters
        ----------
        channel: int
            The channel of the desired servo
        target: int
            The target acceleration in units of quarter-microseconds/10 ms/80 ms

        Notes
        -----
        The range for acceleration is from 0 to 255.
        0 indicates no acceleration limit.
        """
        low: int
        high: int
        low, high = self._get_bits(accel)

        command: str = chr(0x09) + chr(channel) + chr(low) + chr(high)
        self._send_command(command)

    def get_position(self, channel: int) -> int:
        """
        Returns the current position of the servo

        Parameters
        ----------
        channel: int
            The channel number of the desired servo

        Returns
        -------
        position: int
            The current position of the servo in quarter-microseconds
        """
        command: str = chr(0x10) + chr(channel)
        self._send_command(command)
        position: int = self._read_bits()
        return position

    def get_moving_state(self) -> bool:
        """
        States if any servos are currently moving

        Returns
        -------
        response: bool
            True if servos are still moving, False if not

        Notes
        -----
        Only works with Maestro 12, 18, 24
        """
        self._send_command(chr(0x13))
        response: bytes = self.serial.read()
        if response == bytes(0x01):
            return True
        return False

    def get_errors(self) -> int:
        """
        Returns the error code if there are any

        Returns
        -------
        error: int
            The error code
        """
        self._send_command(chr(0x21))
        error: int = self._read_bits()
        return error

    def go_home(self) -> None:
        """
        Sends all servos and outputs to their home positions
        """
        self._send_command(chr(0x22))

    def is_moving(self, channel: int) -> bool:
        """
        Checks if a certain servo is still moving

        Parameters
        ----------
        channel: int
            The channel number of the desired servo

        Returns
        -------
        result: bool
            True if the servo is still moving, False if not
        """
        if self.targets[channel] != -1:
            if self.get_position(channel) != self.targets[channel]:
                return True
        return False


if __name__ == "__main__":
    testMaestro = Maestro()
    testMaestro.set_target(0, 4000)
    testMaestro.set_target(1, 4000)
    testMaestro.set_target(2, 4000)
    testMaestro.set_target(9, 4000)
    testMaestro.set_target(10, 4000)
    testMaestro.get_position(0)
    time.sleep(2)
    testMaestro.set_target(0, 8000)
    testMaestro.set_target(1, 8000)
    testMaestro.set_target(2, 8000)
    testMaestro.set_target(9, 8000)
    testMaestro.set_target(10, 8000)
