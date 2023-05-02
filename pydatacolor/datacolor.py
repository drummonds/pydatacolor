import numpy as np
import struct 
from subprocess import Popen
from time import sleep
import usb.core
from usb.core import USBTimeoutError


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
as not sure how to get raw data.  Starting to think that colorimeter only
gives back raw data per LED, so 6 16bit
    typedef struct {
	char mode;
	float x,y,z;
	float l,a,b;
} CM3_MEASUREMENT;

    """

    def __init__(self, idVendor=0x085c, idProduct=0x0007, verbose=False):
        """dev is usb.core find instance"""
        self.CMD_GET_FIRMWARE_VERSION = 0x02  # Get firmware version (returns 4 bytes)
        self.CMD_SOFT_RESET           = 0x04  # Soft reset (returns nothing)
        self.CMD_MEASURE              = 0x0A  # Measure
        self.CMD_CALIBRATE            = 0x12  # Calibrate
        self.CMD_READ_MEMORY          = 0x16  # Read from CM3 memory
        self.CMD_WRITE_MEMORY         = 0x17  # Write to CM3 memory
        self.EP_BULK_OUT = 0x02
        self.EP_INTERRUPT_IN  = 0x81
        self.EP_BULK_IN  = 0x82
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        # set_configuration not implemented
        if self.dev:
            self.dev.set_configuration()
        if verbose:
            if self.dev is None:
                print ('Our device is not connected')
                raise Exception("No device connected")
            else:
                print(f"Wahhay device is connected \n{self.dev}")
                pass


    def read(self, num_read, timeout=100, timeout_ok=False):
        try:
            result = self.dev.read(self.EP_BULK_IN,num_read,timeout)
        except USBTimeoutError as e:
            if timeout_ok:
                result = []
            else:
                raise e
        return result
    
    def drain(self, verbose = False, timeout=1000):
        """Drain the input buffer use when state is unknown"""
        result = self.read(100, timeout=timeout, timeout_ok=True)
        if result != [] and verbose:
            print(f" Drain got {result}")
    
    def basic_send(self, cmd : bytes, num_read=None, timeout=100):
        # address taken from results of print(dev):   ENDPOINT 0x8: Bulk OUT
        result = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result == len(cmd)
        # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
        result = self.dev.read(self.EP_BULK_IN,num_read,timeout)
        return result
    
    def send(self, cmd: bytes, timeout=100, timeout_ok=False):
        # address taken from results of print(dev):   ENDPOINT 0x8: Bulk OUT
        result_cmd = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result_cmd == len(cmd)
        try:
            result_1 = self.dev.read(self.EP_BULK_IN,2,timeout)
            assert cmd[0] == result_1[0]  # Echos command
            num_read = result_1[1]
            num_to_read = num_read -2
            result_2 = self.dev.read(self.EP_BULK_IN,num_read,timeout)
            if len(result_2) != num_to_read:
                # If timed out try once more
                result_2 += self.dev.read(self.EP_BULK_IN,num_read-len(result),timeout)
            return result_2
        except USBTimeoutError as e:
            if timeout_ok:
                return []
            else:
                raise e

    def interrupt_get(self, cmd: bytes, timeout=100, expect_read_num = 1, timeout_reads = 1000):
        # Uses same bulk out entpoint for sending but pattern afterwards
        # is different
        result_cmd = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result_cmd == len(cmd)
        count = 0
        while count < timeout_reads:
            try:
                result_1 = self.dev.read(self.EP_INTERRUPT_IN,expect_read_num,timeout)
                return result_1
            except USBTimeoutError as e:
                pass
        return []

    def measure(self):
        result = self.send([self.CMD_MEASURE], timeout=200)
        return result
    
    def measure_report(self):
        result = self.send([self.CMD_MEASURE])
        if len(result)  == 13:
            data = struct.unpack("!BHHHHHH", result)
            print(f"Measurement  {data[0]:02x} B1:{data[1]} B2:{data[2]} G1:{data[3]} G2:{data[4]} O:{data[5]} R:{data[6]}")
            # s = 4294967295.0
            s = 65535.0
            # print(f"             B1:{data[1]/s:0.5f} B2:{data[2]/s:0.5f} G1:{data[3]/s:0.5f} G2:{data[4]/s:0.5f} O:{data[5]/s:0.5f} R:{data[6]/s:0.5f}")
        else:
            print(result)
    
    def measure_array_raw(self, num_repeats):
        summary =  np.zeros(shape=(4, num_repeats))
        for n in range(num_repeats):
            result = self.send([self.CMD_MEASURE])
            if len(result)  == 13:
                data = struct.unpack("!Blll", result)
                for i in range(4):
                    summary[i, n] = data[i]/65536
            else:
                print(f" Error result in measure report array {result}")
        return summary
    
    def measure_array_n(self, num_repeats):
        "returns raw LAB values"
        summary =  self.measure_array_raw(num_repeats)
        result = [np.average(summary[1]),np.average(summary[2]),np.average(summary[3])]
        return result

    def measure_report_array(self, num_repeats):
        summary =  self.measure_array_raw()
        print(f"Measurement  xx       L      a*       b*")
        print("       ",end="")
        for i in range(4):
            print(f"{np.average(summary[i]):8.1f} ", end = "")
        print()
        print("       ",end="")
        for i in range(4):
            print(f"{np.std(summary[i]):8.3f} ", end = "")
        print()
    
    def get_int32(self, cmd):
        result = self.send([0x06,0x08,0x16,0x08,0x00,0x0D,0x00,0x04],7)
        serial_num = result[3]*16777216 + result[4]*65536 + result[5]*256 + result[6]   
        return serial_num

    def get_serial_number(self):
        result = self.basic_send(b'\x06\x08\x16\x08\x00\x0D\x00\x04',7)
        serial_num = result[3]*16777216 + result[4]*65536 + result[5]*256 + result[6]   
        return serial_num
    
    def check_result(self,r,expected_result,comment, timeout=100):
        if list(r) != expected_result:
            print(f"Datacolour checking {cmd} got {r} expected {expected_result} : {comment}")
        assert list(r) == expected_result
        return r

    def check(self,cmd,expected_result,comment, timeout=100):
        r = self.send(cmd, timeout=timeout)
        self.check_result(r,expected_result,comment, timeout=100)
        return r
            
    def reset(self):
        self.drain()
        self.drain()
        # Going to check type eg colorimeter to spectrometer
        # Number of sensor bands
        # Details of sensor bands ? nm
        # Lighting formats etc
        self.check([0, 3, 4], [0],"?")
        self.check([1, 3, 2], [0,0,0,0,1],"?")
        self.check([2, 8, 0x16, 8, 0, 0x0B, 0, 2], [0 ,3, 0x68],"firmware version")
        self.check([3, 8, 0x16, 8, 0, 0x18, 0, 1], [0, 6],"?")
        self.check([4, 8, 0x16, 8, 0, 0x26, 0, 1], [0, 0x10],"Soft Reset")
        self.check([5, 8, 0x16, 8, 0, 0x37, 0, 1], [0, 4],"?")
        self.serial_nuber = self.get_serial_number()
        # self.check([6, 8, 0x16, 8, 0, 0x0D, 0, 4], [0, 0, 3, 0xC5, 0x20],"Get serial number")
        self.check([7,3,2], [0,0,0,0,1],"?")
        self.check([8, 8, 0x16, 8, 7, 0xFC, 0, 4], [0, 0, 0, 0, 1],"?")
        self.check([9,3,0x22], [0, 1, 5, 0x0A, 0x0A, 1],"?")
        # This then sees to start a polling loop
        # self.check([], [],"?")

    def wait_for_button_press(self):
        r = self.interrupt_get([0x0A,3,0])
        print(f"Result from button press is {r}")

    def calibrate_send(self, cmd, cmd2, timeout=100, timeout_ok=False):
        """This is a non standard bulk command with 
         - a normal bulk command
        - an extra bulk input
        - a normal bulk input for first command """
        # self.check([0x0B, 8, 0x17, 8, 0, 0x11, 0, 2], [],"Calib ?")
        # self.check([0x10, 0x10], [0],"Calib ?")
        result_cmd = self.dev.write(self.EP_BULK_OUT, list(cmd), timeout)
        assert result_cmd == len(cmd)
        result_2 = self.dev.write(self.EP_BULK_OUT, list(cmd2), timeout)
        assert result_2 == len(cmd2)
        try:
            result_1 = self.dev.read(self.EP_BULK_IN,2,timeout)
            assert cmd[0] == result_1[0]  # Echos command
            num_read = result_1[1]
            num_to_read = num_read -2
            result_2 = self.dev.read(self.EP_BULK_IN,num_read,timeout)
            if len(result_2) != num_to_read:
                # If timed out try once more
                result_2 += self.dev.read(self.EP_BULK_IN,num_read-len(result),timeout)
            return result_2
        except USBTimeoutError as e:
            if timeout_ok:
                return []
            else:
                raise e

    def calibrate(self):
        # Have problems with next two
        self.check_result(
            self.calibrate_send([0x0B, 8, 0x17, 8, 0, 0x11, 0, 2], [0x10, 0x10]),
            [0],
            "Calib E non standard?")
        self.check([0x0C, 3, 4], [0],"Calib C ?")
        self.check([0x0D, 8, 0x16, 8, 3, 0x33, 0, 1], [0, 0x10],"Calib D ?")
        # E actually gets data as the response is variable
        r = self.send([0x0E, 3, 0x0A])
        print(f"E Calibration data = {r}")
        # self.check([0x0E, 3, 0x0A], [0,0,0x66, 0xEC, 0xC4, 0,0,9,0xC4,0xFF, 0xFC, 0xE3, 0xE8],"Calib E ?")
        self.check([0x0F, 4, 0x12, 0], [0],"Calib F ?", timeout=1000)
        # in test got 0,2
        self.check([0x10, 8, 0x16, 8,0, 0xF0,0,0], [0],"Calib 10 orig got 0,2 ?") 
        self.check([0x11, 8, 0x16, 8,0, 0xF1,0,4], [0,0, 8, 0, 0xF9],"Calib 11 ?") 
        self.check_result(
            self.calibrate_send([0x12, 8, 0x17, 8,3, 0x2F,0,4], [0,8,0,0xF9]),
            [0],
            "Calib 12 non standard?")
        self.check_result(
            self.calibrate_send([0x13, 8, 0x17, 8,3, 0x33,0,1], [0x10]),
            [0],
            "Calib 13 non standard?")
        self.check([0x14, 3, 4], [0],"Calib 14 ?")

    def calibration_and_measure(self, num_repeats =100):
        self.calibrate()
        self.white_tile = self.measure_array_n(num_repeats)
        return self.white_tile