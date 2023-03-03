import serial
import ticlib

# I have no idea if this library even works with the maestro board but if it does this should work


def open_airdrop() -> None:
  # Use temp serial port for now until we know
  port: serial.Serial = serial.Serial("/dev/ttyACM0", baud_rate=9600, timeout=0.1, write_timeout=0.1)
  tic = ticlib.TicSerial(port)

  tic.energize()

