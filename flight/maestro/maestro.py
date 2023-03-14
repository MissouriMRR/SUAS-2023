import serial
import time


class Maestro:
    """
    Array with associated photographic information.

    Attributes
    ----------
    exposure : float
        Exposure in seconds.

    Methods
    -------
    colorspace(c='rgb')
        Represent the photo in the given colorspace.
    gamma(n=1.0)
        Change the photo's gamma exposure.
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
        connection_address: str
            The command serial port of the Maestro board (usually '/dev/ttyACM0')

        device_number: int
            The device number that is used to address the board in Pololu Protocol commands
        
        baud_rate: int
            The rate of communication configured for the board (default 9600)
        """
        self.serial = serial.Serial(port=connection_address, baudrate=baud_rate, timeout=0.050)
        self.commandPrefix = chr(0xAA) + chr(device_number)
        self.targets = [-1] * 24

    def _sendCommand(self, command: str) -> None:
        """
        Sends a serial command to the board

        Parameters
        ----------
        command: str
            The command (in bits) to be sent to the board
        """
        self.serial.write(bytes(self.commandPrefix + command, "latin-1"))

    def _getBits(self, integer: int) -> tuple[int, int]:
        """
        Converts an integer value to the 7 high bit, 7 low bit format that the Pololu commands use
        See: https://www.pololu.com/docs/0J40/5.e

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
        """
        low_bits: str = integer & 0x7F
        high_bits: str = (integer >> 7) & 0x7F
        return low_bits, high_bits

    def _readBits(self) -> int:
        """
        Read a 16 bit response from the Maestro board and convert it to an integer

        Returns
        -------
        result: int
            The response from the board
        """
        lsb = ord(self.serial.read())
        msb = ord(self.serial.read())
        return (msb << 8) + lsb

    def setTarget(self, channel: int, target: int) -> None:
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
        low, high = self._getBits(target)
        command = chr(0x04) + chr(channel) + chr(low) + chr(high)

        self._sendCommand(command)
        self.targets[channel] = target

    def setSpeed(self, channel: int, speed: int) -> None:
        """
        Sets the speed limit of the desired servo

        Parameters
        ----------
        channel: int
            The channel of the desired servo

        speed: int
            The speed limit to set the channel to in units of quarter-microseconds/10 ms
        """
        low, high = self._getBits(speed)

        command = chr(0x07) + chr(channel) + chr(low) + chr(high)
        self._sendCommand(command)

    def setAcceleration(self, channel: int, accel: int) -> None:
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
        low, high = self._getBits(accel)

        command = chr(0x09) + chr(channel) + chr(low) + chr(high)
        self._sendCommand(command)

    def getPosition(self, channel: int) -> int:
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
        command = chr(0x10) + chr(channel)
        self._sendCommand(command)
        result = self._readBits()
        print(result)
        return result

    def getMovingState(self) -> bool:
        """
        States if any servos are currently moving

        Returns
        -------
        response: bool
            True if servos are still moving, false if not

        Notes
        -----
        Only works with Maestro 12, 18, 24
        """
        self._sendCommand(chr(0x13))
        response = self.serial.read()
        if response == 0x01:
            return True
        return False

    def getErrors(self) -> int:
        """
        Returns the error code if there are any

        Returns
        -------
        error: int
            The error code
        """
        self._sendCommand(chr(0x21))
        result = self._readBits()
        print(result)
        return result

    def goHome(self) -> None:
        """
        Sends all servos and outputs to their home positions
        """
        self._sendCommand(chr(0x22))

    def isMoving(self, channel) -> bool:
        """
        Checks if a certain servo is still moving

        Parameters
        ----------
        channel: int
            The channel number of the desired servo

        Returns
        -------
        result: bool
            True if the servo is still moving, false if not
        """
        if self.targets[channel] != -1:
            if self.getPosition(channel) != self.targets[channel]:
                return True
        return False


if __name__ == "__main__":
    testMaestro = Maestro()
    testMaestro.setTarget(0, 4000)
    testMaestro.setTarget(1, 4000)
    testMaestro.setTarget(2, 4000)
    testMaestro.setTarget(9, 4000)
    testMaestro.setTarget(10, 4000)
    testMaestro.getPosition(0)
    time.sleep(2)
    testMaestro.setTarget(0, 8000)
    testMaestro.setTarget(1, 8000)
    testMaestro.setTarget(2, 8000)
    testMaestro.setTarget(9, 8000)
    testMaestro.setTarget(10, 8000)
