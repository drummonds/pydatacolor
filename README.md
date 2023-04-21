# pydatacolor
Using Python to connect to Datacolor Spyder Print spectrocolorimeter, SpyderPRINT™

I have made contact but now need to start reading from it.

Note this is version 7 and this https://github.com/drummonds/datacolor1005/blob/master/spectro.c was version 3


# Windows installation
I was stuck for a while as getting the following error

`NotImplementedError: Operation not supported or unimplemented on this platform`

 but then came across this post https://github.com/pyusb/pyusb/discussions/419 and used [Zadig](https://zadig.akeo.ie) to install libusb.


 Option list devices showed dcscusb (v2.0.0.14)
 I upgraded this to WinUSB (v6.1.7600.16385) by click replace driver button.
 
 ![picture 2](images/88518f77b0fe8e1e054f08d46a19c9629e5b950daee6a0d3fcd8c84d7f35957c.png)  

 so now I have:

 ![picture 3](images/256d01002aeefcacd66b1859c35a27e65b79acface94bb89490f0f69104dd721.png)  

This has broken SpyderPrint which only works with its own driver.

My code didn't work return pipe errors but unplugging and replugging got my test code test1.py to work.


I think there is a 16 character buffer on reading.  If you don't read all the data then this buffer wil fill up and if it gets to the limit a USB Pipe error is created.

Thre is still a lot of magic in this see test3.py.

Commands:
- 00x
- 01x
- 02x
- 03x
- 04x
- 05x
- 06x: Get serial number
- 07x
- 08x
- 09x
- 0Ax  Measure?
- 0Bx
- 0Cx  Calibrate?
- 0Dx
- 0Ex
- 0Fx






