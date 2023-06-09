import struct
from time import sleep
import usb.core
from usb.core import USBTimeoutError


dev = usb.core.find()
"""Aim to improve test.py to take a measurement precursor to createing a modulegit"""


class DataColor:
    """According to http://www.linux-usb.org/usb.ids
        Vendor IDS are
    085c  ColorVision, Inc.
            0100  Spyder 1
            0200  Spyder 2
            0300  Spyder 3

    The output of printing dev was you have found your device is:
    DEVICE ID 085c:0007 on Bus 001 Address 008 =================
     bLength                :   0x12 (18 bytes)
     bDescriptorType        :    0x1 Device
     bcdUSB                 :  0x110 USB 1.1
     bDeviceClass           :    0x0 Specified at interface
     bDeviceSubClass        :    0x0
     bDeviceProtocol        :    0x0
     bMaxPacketSize0        :   0x40 (64 bytes)
     idVendor               : 0x085c
     idProduct              : 0x0007
     bcdDevice              :    0x0 Device 0.0
     iManufacturer          :    0x1 Error Accessing String
     iProduct               :    0x2 Error Accessing String
     iSerialNumber          :    0x0
     bNumConfigurations     :    0x1
      CONFIGURATION 1: 64 mA ===================================
       bLength              :    0x9 (9 bytes)
       bDescriptorType      :    0x2 Configuration
       wTotalLength         :   0x27 (39 bytes)
       bNumInterfaces       :    0x1
       bConfigurationValue  :    0x1
       iConfiguration       :    0x0
       bmAttributes         :   0x80 Bus Powered
       bMaxPower            :   0x20 (64 mA)
        INTERFACE 0: Reserved ==================================
         bLength            :    0x9 (9 bytes)
         bDescriptorType    :    0x4 Interface
         bInterfaceNumber   :    0x0
         bAlternateSetting  :    0x0
         bNumEndpoints      :    0x3
         bInterfaceClass    :    0x0 Reserved
         bInterfaceSubClass :    0x0
         bInterfaceProtocol :    0x0
         iInterface         :    0x0
          ENDPOINT 0x81: Interrupt IN ==========================
           bLength          :    0x7 (7 bytes)
           bDescriptorType  :    0x5 Endpoint
           bEndpointAddress :   0x81 IN
           bmAttributes     :    0x3 Interrupt
           wMaxPacketSize   :    0x8 (8 bytes)
           bInterval        :    0xa
          ENDPOINT 0x82: Bulk IN ===============================
           bLength          :    0x7 (7 bytes)
           bDescriptorType  :    0x5 Endpoint
           bEndpointAddress :   0x82 IN
           bmAttributes     :    0x2 Bulk
           wMaxPacketSize   :    0x8 (8 bytes)
           bInterval        :    0x0
          ENDPOINT 0x2: Bulk OUT ===============================
           bLength          :    0x7 (7 bytes)
           bDescriptorType  :    0x5 Endpoint
           bEndpointAddress :    0x2 OUT
           bmAttributes     :    0x2 Bulk
           wMaxPacketSize   :    0x8 (8 bytes)
           bInterval        :    0x0


    /// Calibration modes
    typedef enum {
            CM3_CAL_WHITE					= 0,		///< Calibrate from white tile
            CM3_CAL_BLACK					= 1			///< Calibrate from black tile (not used)
    } CM3_CAL_TYPE;

    Measurement is either xyz or lab but so requires to be calibrated first
    as not sure how to get raw data.
        typedef struct {
            char mode;
            float x,y,z;
            float l,a,b;
    } CM3_MEASUREMENT;

    """

    def __init__(self, idVendor=0x085C, idProduct=0x0007, verbose=False):
        """dev is usb.core find instance"""
        self.CMD_GET_FIRMWARE_VERSION = 0x02  # Get firmware version (returns 4 bytes)
        self.CMD_SOFT_RESET = 0x04  # Soft reset (returns nothing)
        self.CMD_MEASURE = 0x0A  # Measure
        self.CMD_CALIBRATE = 0x12  # Calibrate
        self.CMD_READ_MEMORY = 0x16  # Read from CM3 memory
        self.CMD_WRITE_MEMORY = 0x17  # Write to CM3 memory
        self.EP_BULK_OUT = 0x02
        self.EP_BULK_IN = 0x82
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        # set_configuration not implemented
        if self.dev:
            self.dev.set_configuration()
        if verbose:
            if self.dev is None:
                print("Our device is not connected")
                raise Exception("No device connected")
            else:
                print(f"Wahhay device is connected \n{self.dev}")
                pass

    def read(self, num_read, timeout=100, timeout_ok=False):
        try:
            result = self.dev.read(self.EP_BULK_IN, num_read, timeout)
        except USBTimeoutError as e:
            if timeout_ok:
                result = []
            else:
                raise e
        return result

    def drain(self, verbose=False, timeout=1000):
        """Drain the input buffer use when state is unknown"""
        result = self.read(100, timeout=timeout, timeout_ok=True)
        if result != [] and verbose:
            print(f" Drain got {result}")

    def basic_send(self, cmd: bytes, num_read=None, timeout=100):
        # address taken from results of print(dev):   ENDPOINT 0x8: Bulk OUT
        result = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result == len(cmd)
        # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
        result = self.dev.read(self.EP_BULK_IN, num_read, timeout)
        return result

    def send(self, cmd: bytes, timeout=100, timeout_ok=False):
        # address taken from results of print(dev):   ENDPOINT 0x8: Bulk OUT
        result_cmd = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result_cmd == len(cmd)
        try:
            result_1 = self.dev.read(self.EP_BULK_IN, 2, timeout)
            assert cmd[0] == result_1[0]  # Echos command
            num_read = result_1[1]
            num_to_read = num_read - 2
            result_2 = self.dev.read(self.EP_BULK_IN, num_read, timeout)
            if len(result_2) != num_to_read:
                # If timed out try once more
                result_2 += self.dev.read(
                    self.EP_BULK_IN, num_read - len(result), timeout
                )
            return result_2
        except USBTimeoutError as e:
            if timeout_ok:
                return []
            else:
                raise e

    def measure(self):
        result = dc.send([self.CMD_MEASURE], timeout=200)
        return result

    def measure_report(self):
        result = dc.send([self.CMD_MEASURE])
        if len(result) == 13:
            data = struct.unpack("!BIII", result)
            print(f"Measurement  {data[0]:02x} l:{data[1]} a:{data[2]} b:{data[3]}")
            s = 4294967295.0
            print(
                f"             {data[0]:02x} l:{data[1]/s} a:{data[2]/s} b:{data[3]/s}"
            )
        else:
            print(result)

    def get_int32(self, cmd):
        result = self.send([0x06, 0x08, 0x16, 0x08, 0x00, 0x0D, 0x00, 0x04], 7)
        serial_num = (
            result[3] * 16777216 + result[4] * 65536 + result[5] * 256 + result[6]
        )
        return serial_num

    def get_serial_number(self):
        result = self.basic_send(b"\x06\x08\x16\x08\x00\x0D\x00\x04", 7)
        serial_num = (
            result[3] * 16777216 + result[4] * 65536 + result[5] * 256 + result[6]
        )
        return serial_num


def show_result(name, result, suffix=""):
    print(f"{name:40} ", end="")
    for b in result:
        print(f"{b:02X} ", end="")
    print(" " + suffix)


dc = DataColor(verbose=True)
dc.drain(verbose=True)
dc.drain(verbose=True)  # Safety check
print(f"Serial num = {dc.get_serial_number()}")
dc.drain(verbose=True)
cmd = [0, 3, 4]
result = dc.send([0, 3, 4])
print("=" * 80 + "\n  Initialisation\nNumbers in hex")
show_result(f"0 []                  (0)", dc.send([0, 3, 4]), "?")
show_result(f"1 [02]                (0,0,0,0,1)", dc.send([1, 3, 2], timeout=100), "?")
show_result(
    f"2 [16 08 00 0B 00 02] (00 03 68)",
    dc.send([2, 8, 0x16, 8, 0, 0x0B, 0, 2]),
    "firmware version",
)
show_result(
    f"3 [16 08 00 18 00 01] (00 06)", dc.send([3, 8, 0x16, 8, 0, 0x18, 0, 1]), "?"
)
show_result(
    f"4 [16 08 00 26 00 01] (00 10)",
    dc.send([4, 8, 0x16, 8, 0, 0x26, 0, 1]),
    "Soft reset?",
)
show_result(
    f"5 [16 08 00 37 00 01] (00 04)", dc.send([5, 8, 0x16, 8, 0, 0x37, 0, 1]), "?"
)
show_result(
    f"6 [16 08 00 37 00 01] (00 00 03 C5 20)",
    dc.send([6, 8, 0x16, 8, 0, 0x0D, 0, 4]),
    "?",
)
show_result(f"7 [02]                (0,0,0,0,1)", dc.send([7, 3, 2], timeout=100), "?")
show_result(
    f"8 [16 08 07 FC 00 04] (00 00 03 C5 20)",
    dc.send([8, 8, 0x16, 8, 7, 0xFC, 0, 4]),
    "?",
)
show_result(
    f"9 [22]                (00 01 05 0A 0A 01)",
    dc.send([9, 3, 0x22], timeout=100),
    "?",
)
show_result(
    f"A [02]                ()",
    dc.send([0x0A, 3, 0], timeout=100, timeout_ok=True),
    "?",
)

dc.drain(verbose=True)
print("=" * 80 + "\n  Calibration")
print("=" * 80 + "\n  Measurement")
for i in range(2):
    result = dc.measure()
    show_result(f"Measured {i}", result)
    sleep(0.2)
for i in range(2):
    dc.measure_report()
    sleep(0.5)
for i in range(3):
    result = dc.read(1, timeout=100, timeout_ok=True)
    show_result(f"Read {i}", result)

print("Done this")
