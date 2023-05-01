"""
This is the first of development phase and using the rough framework.  Test5 should be the same as
test4 but using the local library.
"""

import numpy as np
import struct 
from subprocess import Popen
from time import sleep
import usb.core
from usb.core import USBTimeoutError

from pydatacolor import DataColor


dev = usb.core.find()
"""Aim to improve test.py to take a measurement precursor to createing a modulegit"""



from textual.app import App, ComposeResult
from textual.widgets import Static


class PrideApp(App):
    """Displays a pride flag."""

    COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]

    def compose(self) -> ComposeResult:
        for color in self.COLORS:
            stripe = Static()
            stripe.styles.height = "1fr"
            stripe.styles.background = color
            yield stripe


if __name__ == "__main__":
    PrideApp().run()


def show_result(name, result, suffix = ""):
    print(f"{name:40} ", end = "")
    for b in result:
        print(f"{b:02X} ", end = "")
    print(" " + suffix)
    
dc = DataColor(verbose=False)
dc.reset()
print(f"Serial number = {dc.serial_nuber}")
            
dc.drain(verbose=True)
# The following was to synchronise and try get pictures
# if not camera will just fail silently
# pid = Popen(["poetry", "run", "python", "testcam.py"]).pid
# sleep(2)  # Try to align first meausurement snap  after 1 sec 
# print(f"Started webcam snap {pid}", flush=True)
print("="*80 + "\n  Calibration  Press button on continue", flush=True)
dc.wait_for_button_press()
dc.calibrate()
print("="*80 + "\n  Measurement press button to continue", flush=True)
for i in range(26):
    dc.wait_for_button_press()
    dc.measure_report_array(100)

print("Done this", flush=True)