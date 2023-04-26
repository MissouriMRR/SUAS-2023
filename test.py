from flight.test_files.state_machine_test import run_test
import asyncio
from communication import Communication


comm = Communication()

print(comm.state())

asyncio.run(run_test(True))

