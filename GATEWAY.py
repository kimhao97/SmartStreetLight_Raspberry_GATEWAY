import serial 
import time
import GATEWAY_CONST as CONST
print("GATEWAY's running....")
usb_Serial = serial.Serial(             
							 port='/dev/ttyUSB1',
							 baudrate = 9600,
							 parity=serial.PARITY_NONE,
							 stopbits=serial.STOPBITS_ONE,
							 bytesize=serial.EIGHTBITS,
							 timeout=1
		)

def CRCvalue(loraData):
	temp = 0
	for i in range(0, CONST.LORA_DATA_RANGE - 1):
		try:
			temp += loraData[i]
		except:
			print("ERROR CRC")
	return (temp & 0xff)

def checkLoraReceive(loraData, adrr_a, adrr_b, adrr_c):
	if loraData[22] == CRCvalue(loraData):
		if loraData[0] == adrr_a and loraData[1] == adrr_b and loraData[2] == adrr_c:
			return True
		else: return False

def voltagePZEM(data):
	return (data[3] << 8) + data[4] + (data[5] / 10.0)
def currentPZEM(data):
	return (data[6] + (data[7] / 100.0))
def powerPZEM(data):
	return (data[8] << 8) + data[9]
def energyPZEM(data):
	return (data[10] << 16) + (data[11] << 8) + data[12]

def waterLevel(data):
	temp = 0
	for i in range(13,17):
		temp = temp*10 + (data[i] - ord('0'))
	return temp #cm

def humidity(data):
	return data[17] + data[18] / 10.0;
def temperature(data):
	return data[19] + data[20] / 10.0;
def weather(data):
	return data[21]

dataLoraReceive = list()
while 1:
	if usb_Serial.inWaiting()>0:
		dataLoraReceive = usb_Serial.readline()
		print(dataLoraReceive)
		print(dataLoraReceive[22])	
		print(CRCvalue(dataLoraReceive))
		print(checkLoraReceive(dataLoraReceive, CONST.LIGHT_1_A, CONST.LIGHT_1_B, CONST.LIGHT_1_C))
		print(voltagePZEM(dataLoraReceive))
		print(currentPZEM(dataLoraReceive))
		print(powerPZEM(dataLoraReceive))
		print(energyPZEM(dataLoraReceive))
		print("waterLevel = {}". format(waterLevel(dataLoraReceive)))	
		print("humidity = {}".format(humidity(dataLoraReceive)))
		print("temperature = {}". format(temperature(dataLoraReceive)))	