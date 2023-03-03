import serial

class Maestro:
    def __init__(self, connectionAddress: str = '/dev/ttyACM0'):
        self.serialPort = serial.Serial(port=connectionAddress, baudrate=9600, timeout=0.050)

    def setPosition() -> None:
        # TODO
        return
