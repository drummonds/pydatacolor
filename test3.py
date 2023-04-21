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

    """

    def __init__(self, idVendor=0x085c, idProduct=0x0007, verbose=False):
        """dev is usb.core find instance"""
        self.CMD_GET_FIRMWARE_VERSION = 0x02  # Get firmware version (returns 4 bytes)
        self.CMD_SOFT_RESET           = 0x04  # Soft reset (returns nothing)
        self.CMD_MEASURE              = 0x0A  # Measure
        self.CMD_CALIBRATE            = 0x12  # Calibrate
        self.CMD_READ_MEMORY          = 0x16  # Read from CM3 memory
        self.CMD_WRITE_MEMORY         = 0x17  # Write to CM3 memory
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        # set_configuration not implemented
        if self.dev:
            self.dev.set_configuration()
        if verbose:
            if self.dev is None:
                print ('Our device is not connected')
            else:
                print(f"Wahhay device is connected \n{self.dev}")
                pass


    def read(self, num_read, timeout=100, timeout_ok=False):
        try:
            result = self.dev.read(0x82,num_read,timeout)
        except USBTimeoutError as e:
            if timeout_ok:
                result = []
            else:
                raise e
        return result
    
    def send(self, cmd, num_read):
        # address taken from results of print(dev):   ENDPOINT 0x8: Bulk OUT
        result = self.dev.write(0x2, cmd, 100)
        assert result == len(cmd)
        # self.dev.write(0x2,cmd)
        # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
        result = self.dev.read(0x82,num_read,1000)
        return result
    
    def measure(self):
        result = dc.send([self.CMD_MEASURE],15)
        return result
    
    def get_serial_number(self):
        result = self.send([0x06,0x08,0x16,0x08,0x00,0x0D,0x00,0x04],7)
        serial_num = result[3]*16777216 + result[4]*65536 + result[5]*256 + result[6]   
        return serial_num
    
def show_result(name, result):
    print(f"{name} ", end = "")
    for b in result:
        print(f"{b:02X} ", end = "")
    print("")
    
dc = DataColor(verbose=True)
print(f"Serial num = {dc.get_serial_number()}")
cmd = [0, 3, 4]
result = dc.send(cmd,3)
show_result("Returned (0,3,0)", result)
show_result(f"  Check empty", dc.read(1,timeout=1000, timeout_ok=True))
show_result("Step 006 (1,7,0,0,0,0,1)",dc.send([1,3,2],7))
show_result(f"  Check empty", dc.read(1,timeout=1000, timeout_ok=True))
show_result("Step 010 (2,0,5,3,68)",dc.send([2, 8, 0x16, 8, 0, 0x0B, 0, 2],5))
show_result(f"  Check empty", dc.read(1,timeout=1000, timeout_ok=True))
for i in range(2):
    result = dc.measure()
    show_result(f"Measured {i}", result)
    show_result(f"  Check empty", dc.read(1,timeout=1000, timeout_ok=True))
    sleep(2)
for i in range(3):
    result = dc.read(1,timeout=1000, timeout_ok=True)
    show_result(f"Read {i}", result)

print("Done this")