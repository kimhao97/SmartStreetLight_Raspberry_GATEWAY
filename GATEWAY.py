import serial 
import time
print("Begin....")
usb_Serial = serial.Serial(             
               port='/dev/ttyUSB3',
               baudrate = 9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
    )

while 1:

	if usb_Serial.inWaiting()>0:
		x=usb_Serial.readline()
		print(x)