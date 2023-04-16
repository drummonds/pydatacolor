import usb.core
dev = usb.core.find()
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
    print(f"Wahhay device is connected {dev}")



print("Done this")