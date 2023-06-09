"""This is an asynchronous higher level model to the core pydatacolor.

The state is modelled as a finite state machine.  Some states
have duration and will change attributes during that state.  So from a front end
point of view they need monitoring, others are static and don't need monitoring.
"""
import asyncio
from enum import Enum

from lofigui import reset, print
from .datacolor import DataColor


class DataColorState(Enum):
    Disconnected = 1
    Connecting = 2  # Requires polling
    Connected = 3
    Calibrating = 4  # Requires polling
    Calibrated = 5  # Now ready for use but with no data
    Measureing = 6  # Now read for use, Requires polling
    Measured = 7  # Has data, ready for use
    Failed = 8  # eg timeout during normal process
    NotFound = 9  # eg timeout during normal process


class DataColorModel:
    """Async model class for datacolour, the transitions will only work from the correct state"""

    def __init__(self):
        self.state = DataColorState.Disconnected
        self.run_count = 0
        self.datacolor = None

    def connect(self):
        "Model code interacting with colourimeter"
        if self.state == DataColorState.Disconnected:
            self.state = DataColorState.Connecting
            reset()
            print(f"Test colourimeter")
            self.datacolor = DataColor(verbose=False)
            self.datacolor._print = print
            if self.datacolor.dev:
                print(f"Reset colourimeter")
                self.datacolor.reset()
                print(f"Drain colourimeter")
                self.datacolor.drain(verbose=False)
                print(f"Serial number = {self.datacolor.get_serial_number()}")
                print(f"Drain colourimeter")
                self.state = DataColorState.Connected
            else:
                print(f"No colourimeter found")
                self.state = DataColorState.NotFound

    def calibrate(self):
        "Model code interacting with colourimeter"
        if self.state in [DataColorState.Connected, DataColorState.Measured]:
            self.state = DataColorState.Calibrating
            self.datacolor.calibrate()
            self.state = DataColorState.Calibrated

    def measure(self):
        "Model code interacting with colourimeter"
        if self.state in [DataColorState.Calibrated, DataColorState.Measured]:
            self.state = DataColorState.Measureing
            self.datacolor.measure_report_array(100)
            self.state = DataColorState.Measured

    def stop(self):
        self.run = False
