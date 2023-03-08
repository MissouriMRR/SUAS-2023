import serial

class Maestro:
    def __init__(self, connection_address: str = '/dev/ttyACM0', device_number: int = 12, baud_rate: int = 9600):
        self.serial = serial.Serial(port=connection_address, baudrate=baud_rate, timeout=0.050)
        self.commandPrefix = chr(0xAA) + chr(device_number)
        self.targets = [-1] * 24

    def _sendCommand(self, command: str) -> None:
        self.serial.write(bytes(self.commandPrefix + command, 'latin-1'))

    def _getBits(self, integer: int):
        low_bits = integer & 0x7F
        high_bits = (integer >> 7) & 0x7F
        return low_bits, high_bits
    
    def _readBits(self) -> int:
        lsb = ord(self.serial.read())
        msb = ord(self.serial.read())
        return (msb << 8) + lsb

    def setTarget(self, channel: int, target: int) -> None:
        low, high = self._getBits(target)

        command = chr(0x04) + chr(channel) + chr(low) + chr(high)
        self._sendCommand(command)
        self.target[channel] = target

    def setSpeed(self, channel: int, speed: int) -> None:
        low, high = self._getBits(speed)

        command = chr(0x07) + chr(channel) + chr(low) + chr(high)
        self._sendCommand(command)

    def setAcceleration(self, channel: int, accel: int) -> None:
        low, high = self._getBits(accel)

        command = chr(0x09) + chr(channel) + chr(low) + chr(high)
        self._sendCommand(command)

    def getPosition(self, channel: int):
        command = chr(0x10) + chr(channel)
        self._sendCommand(command)
        result = self._readBits()
        print(result)
        return result

    def getMovingState(self) -> bool:
        # Only works with Maestro 12, 18, 24
        self._sendCommand(chr(0x13))
        response = self.serial.read()
        if response == 0x01:
            return True
        return False
    
    def getErrors(self):
        self._sendCommand(chr(0x21))
        result = self._readBits()
        print(result)
        return result

    def goHome(self):
        self._sendCommand(chr(0x22))

    def isMoving(self, channel) -> bool:
        if self.targets[channel] != -1:
            if self.getPosition(channel) != self.targets[channel]:
                return True
        return False
                 
    # TODO:
    # Stop Script
    # Restart Script
    # Restart Script with Parameter
    # Get Script Status

if __name__ == "__main__":
    testMaestro = Maestro()
    testMaestro.getPosition(0)
    testMaestro.setTarget(0, 5000)



