import serial 
import time
print("GATEWAY's running....")
usb_Serial = serial.Serial(             
               port='/dev/ttyUSB1',
               baudrate = 9600,
               parity=serial.PARITY_NONE,
               stopbits=serial.STOPBITS_ONE,
               bytesize=serial.EIGHTBITS,
               timeout=1
    )

dataLoraRceive = list()
while 1:
  global dataLoraRceive
	if usb_Serial.inWaiting()>0:
		dataLoraRceive=usb_Serial.readline()
    print(dataLoraRceive[1])
  print(dataLoraRceive[2])
  