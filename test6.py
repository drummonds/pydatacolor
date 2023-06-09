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

"""Aim to really simple measurement app"""


from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Footer, Header, Static


class ColourDisplay(Static):
    """A widget to display a measured colour."""


class Calibrate(Static):
    """A colour measurement widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "calibrate":
            if "started" in self.classes:
                self.remove_class("started")
            else:
                self.app.add_colourimeter()
                if self.app.dc:
                    r = self.get_child_by_id("calibresult")
                    tile = self.app.dc.calibration_and_measure()
                    r.update(f"White = {tile} SN = {self.app.dc.get_serial_number()}")
                    self.add_class("started")

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Calibrate", id="calibrate", variant="success")
        yield ColourDisplay("#FF0000", id="calibresult")


class Measurement(Static):
    """A colour measurement widget."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "measure":
            if "started" in self.classes:
                self.remove_class("started")
            else:
                if self.app.dc:
                    r = self.get_child_by_id("result")
                    tile = self.app.dc.measure_array_n(100)
                    r.update(f"L*ab = {tile}")
                    self.add_class("started")

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield Button("Measure", id="measure", variant="success")
        yield ColourDisplay("#FFEFDF", id="result")


class Measurer(App):
    """A Textual app to calibrate and make measurements with a Datacolor Colorimeter."""

    CSS_PATH = "test6.css"
    BINDINGS = [("q", "quit", "Quit the app"), ("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield ScrollableContainer(Calibrate(), Measurement(), Measurement())
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def add_colourimeter(self):
        self.dev = usb.core.find()
        self.dc = DataColor(verbose=False)
        if self.dc:
            self.dc.reset()
            # print(f"Serial number = {dc.serial_nuber}")

            self.dc.drain(verbose=False)


if __name__ == "__main__":
    app = Measurer()
    app.run()
