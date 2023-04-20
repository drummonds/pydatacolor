import usb.core
dev = usb.core.find()


class DataColor:

    def __init__(self, dev):
        """dev is usb.core find instance"""
        self.dev = dev
        self.CMD_GET_FIRMWARE_VERSION = 0x02  # Get firmware version (returns 4 bytes)
        self.CMD_SOFT_RESET           = 0x04  # Soft reset (returns nothing)
        self.CMD_MEASURE              = 0x0A  # Measure
        self.CMD_CALIBRATE            = 0x12  # Calibrate
        self.CMD_READ_MEMORY          = 0x16  # Read from CM3 memory
        self.CMD_WRITE_MEMORY         = 0x17  # Write to CM3 memory

    def command(self, code, msg = "", num_out=None):
        if num_out == None:
        	num_out = len(msg)
        self.dev.write(code, msg, num_out)
        ret = self.dev.read(code+128, len(msg), 100)
        sret = ''.join([chr(x) for x in ret])
        print(f"Cmd {code} = {sret}")
        return sret

# 	unsigned char buf[256];
# 	static unsigned char cm3_command_tag = 0;
# 	unsigned char tag_this, status;
# 	int err, pos, count;

# 	assert(len != NULL);
# 	assert(*len >= 0);
# 	assert(*len < ((int)sizeof(buf)-3));

# 	/***
# 	 * Packet format:
# 	 * <TAG> <LEN> <CMD> <PAYLOAD>
# 	 */
# 	buf[0] = tag_this = cm3_command_tag;
# 	buf[1] = *len + 3;  // Counts the 3-byte header too
# 	buf[2] = cmd;

# 	cm3_command_tag = (cm3_command_tag + 1) & 0x7F;

# 	// Copy in the payload
# 	if (*len > 0) {
# 		memcpy(&buf[3], payload, *len);
# 	}


# >>> msg = 'test'
# >>> assert len(dev.write(1, msg, 100)) == len(msg)
# >>> ret = dev.read(0x81, len(msg), 100)
# >>> sret = ''.join([chr(x) for x in ret])
# >>> assert sret == msg

# 	// Send command
# 	pos = 0;
# 	while (pos < (*len + 3)) {
# 		// 1-sec timeout
# 		err = libusb_bulk_transfer(devh, 2 | LIBUSB_ENDPOINT_OUT, &buf[pos], (*len + 3) - pos, &count, 1000);
# 		if ((err != 0) && (err != LIBUSB_ERROR_TIMEOUT)) {
# 			fprintf(stderr, "Error %d (%s) during EP OUT command transfer\n", err, libusb_error_name(err));
# 			return -1;
# 		}
# 		pos += count;
# 	}

# 	// Receive response
# 	err = libusb_bulk_transfer(devh, 2 | LIBUSB_ENDPOINT_IN, buf, sizeof(buf), &count, 1000);
# 	if (err != 0) {
# 		fprintf(stderr, "Error %d (%s) during EP IN transfer\n", err, libusb_error_name(err));
# 		return -1;
# 	}

# 	// Make sure tag matches the one we sent
# 	if (buf[0] != tag_this) {
# 		fprintf(stderr, "WARNING: Mismatched tag in response\n");
# 	}

# 	// Save status code and length
# 	status = buf[2];
# 	*len = buf[1] - 3;

# 	// Copy the rest of the payload (if any)
# 	if ((*len > 0) && (response != NULL)) {
# 		memcpy(response, &buf[3], *len);
# 	}

# 	return status;
# }

    def get_firmware_version(self):
        """Get firmware version"""
        v = self.command(self.CMD_GET_FIRMWARE_VERSION)
        return v


# 	err = cm3_cmd(devh, CM3_CMD_GET_FIRMWARE_VERSION, NULL, &len, buf);
# 	if (err == 0) {
# 		*ver = 0;
# 		for (int i=0; i<4; i++) {
# 			*ver = (*ver << 8) + buf[i];
# 		}
# 	}

# 	return err;
# }

printers = usb.core.find(find_all=True, bDeviceClass=7)
count = 0
for printer in printers:
    print(printer)
    count += 1
print(f'There are {count} printers in the system')
devices = usb.core.find(find_all=True, bDeviceClass=7)
count = 0
for device in devices:
    print(device)
    count += 1
print(f'There are {count} devices  in the system')
dev = usb.core.find(idVendor=0x085c, idProduct=0x0007)
if dev is None:
    print ('Our device is not connected')
else:
    print(f"Wahhay device is connected \n{dev}")
dc = DataColor(dev)
dc.get_firmware_version()


print("Done this")