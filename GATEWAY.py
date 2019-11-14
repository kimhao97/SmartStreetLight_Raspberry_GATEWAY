import serial 
import time
import GATEWAY_CONST as CONST
from firebase import firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import serial.tools.list_ports

print("GATEWAY's setting....")
databaseURL =  'https://nckh-firebase.firebaseio.com/'
firebaseCertFile = "/home/pi/SmartStreetLight_Raspberry_GATEWAY/nckh-firebase-firebase-adminsdk-auqm0-e08b1006f2.json"

if (not len(firebase_admin._apps)):
    cred = credentials.Certificate(firebaseCertFile)    
    firebase_admin.initialize_app(cred, {'databaseURL': databaseURL})

# ports = list(serial.tools.list_ports.comports())
# for p in ports:
# 	if("FT232R USB UART" in p):
# 		usbFTD = str(p).split(' ')			
# print(usbFTD[0])
usb_Serial = serial.Serial(             
							 port='/dev/ttyUSB3',
							 baudrate = 9600,
							 parity=serial.PARITY_NONE,
							 stopbits=serial.STOPBITS_ONE,
							 bytesize=serial.EIGHTBITS,
							 timeout=1
		)
print("GATEWAY's running....")
def updateDataToFirebase(loraData, light_addr_a, ligh_addr_b, light_addr_c):
	global txt
	txt +=1
	if checkLoraReceive(loraData, light_addr_a, ligh_addr_b, light_addr_c):
		setPowerFirebase(powerPZEM(loraData), 1)
		setEnergyFirebase(energyPZEM(loraData), 1)
		setDimFirebase(dimData(loraData), 1)
		setHumidityFirebase(humidity(loraData))
		setTemperatureFirebase(temperature(loraData))
		setWaterLevelFirebase(waterLevel(loraData))
		setRainLevelFirebase(weather(loraData))
		db.reference('Smartlight/sensors/test').set(txt)
		return 1
	else: 
		return 0

def setPowerFirebase(data, lightPosition):
	db.reference('Smartlight/power/watt_%s'%(str(lightPosition))).set(data)
def setEnergyFirebase(data, lightPosition):
	db.reference('Smartlight/power/consumpt_%s'%(str(lightPosition))).set(data)
def setDimFirebase(data, lightPosition):
	db.reference('Smartlight/dimmer/light_%s'%(str(lightPosition))).set(data)	
def setHumidityFirebase(data):
	db.reference('Smartlight/sensors/humidity').set(data)
def setTemperatureFirebase(data):
	db.reference('Smartlight/sensors/temperature').set(data)
def setWaterLevelFirebase(data):
	db.reference('Smartlight/sensors/water level').set(data)
def setRainLevelFirebase(data):
	db.reference('Smartlight/sensors/rain').set(data)
def setNotification(data):
	db.reference('Smartlight/notification').set(data)

def checkLoraReceive(loraData, adrr_a, adrr_b, adrr_c):
	if len(loraData) == CONST.LORA_DATA_RANGE:
		if loraData[CONST.CRC_LOCATION] == CRCvalue(loraData, CONST.LORA_DATA_RANGE):
			if loraData[0] == adrr_a and loraData[1] == adrr_b and loraData[2] == adrr_c:
				return 1
	else: 
		return 0

def CRCvalue(loraData, size):
	temp = 0
	for i in range(0, size - 1):
		try:
			temp += loraData[i]
		except:
			print("ERROR CRC")
	return (temp & 0xff)

def voltagePZEM(data):	
	t = (data[3] << 8) + data[4] + (data[5] / 10.0)
	if t >= CONST.MIN_AC_VOLTAGE and t <= CONST.MAX_AC_VOLTAGE :
		return t
	else: return CONST.ERROR_PZEM
def currentPZEM(data):
	return (data[6] + (data[7] / 100.0))
def powerPZEM(data):
	return (data[8] << 8) + data[9]
def energyPZEM(data):
	return (data[10] << 16) + (data[11] << 8) + data[12]
def dimData(data):
	return data[22]

def waterLevel(data):
	temp = 0
	for i in range(13,17):
		temp = temp*10 + (data[i] - ord('0'))
	if temp > CONST.MIN_WATER_LEVEL and temp < CONST.MAX_WATER_LEVEL:
		return temp #cm	
	else: return CONST.ERROR_WATER_SENSOR

def humidity(data):
	return data[17] + data[18] / 10.0;
def temperature(data):
	return data[19] + data[20] / 10.0;
def weather(data):
	if data[21] == CONST.RAINY:
		return True
	else: return False

def dataUpdateRequest():
	global timeBegin
	if (millis() - timeBegin) > CONST.TIME_OUT:
		timeBegin = millis()
		rData = sendDataUpdateRequest(CONST.LIGHT_1_A, CONST.LIGHT_1_B, CONST.LIGHT_1_C)
		if rData : 
			pass
		else: setNotification("SENDING ERROR")
def sendDataUpdateRequest(adrr_a, adrr_b, adrr_c):
	data = [adrr_a, adrr_b, adrr_c, 0x00]
	data.append(CRCvalue(data, 5))
	dataSend = bytearray(data)
	usb_Serial.write(dataSend)
	usb_Serial.flush()
	counter = 1
	refundValue = 0
	while counter <= CONST.COUNT_LIMIT and refundValue == 0:
		counter +=1
		return receiveLoraData(2000)		
def receiveLoraData(timeout):
	dataLoraReceive = list()
	startTime = millis()
	while (millis() - startTime) <= timeout:
		# print("__________________________________")
		if usb_Serial.inWaiting()>0:
			dataLoraReceive = usb_Serial.readline()	
			print(dataLoraReceive)
			print("Length = {}".format(len(dataLoraReceive)))
			return updateDataToFirebase(dataLoraReceive, CONST.LIGHT_1_A, CONST.LIGHT_1_B, CONST.LIGHT_1_C)		
	return  0 

def millis():
    return round(time.time()*1000)

txt = 0
timeBegin = millis()
while 1:	
	dataUpdateRequest()

	# usb_Serial.write(bytes([0xC1]))
	# usb_Serial.flush()
	# time.sleep(2)

	# if usb_Serial.inWaiting()>0:
	# 	dataLoraReceive = usb_Serial.readline()	
	# 	print("Here")
	# 	print(dataLoraReceive)
	# 	print("Length = {}".format(len(dataLoraReceive)))
	# 	updateDataToFirebase(dataLoraReceive, CONST.LIGHT_1_A, CONST.LIGHT_1_B, CONST.LIGHT_1_C)

		# print(dataLoraReceive[23])	
		# print(CRCvalue(dataLoraReceive))
		# print(checkLoraReceive(dataLoraReceive, CONST.LIGHT_1_A, CONST.LIGHT_1_B, CONST.LIGHT_1_C))
		# print(voltagePZEM(dataLoraReceive))
		# print(currentPZEM(dataLoraReceive))
		# print(powerPZEM(dataLoraReceive))
		# print(energyPZEM(dataLoraReceive))
		# print("waterLevel = {}". format(waterLevel(dataLoraReceive)))	
		# print("humidity = {}".format(humidity(dataLoraReceive)))
		# print("temperature = {}". format(temperature(dataLoraReceive)))	
		# print("dim = {}".format(dataLoraReceive[22]))

		# print("firebase = {}".format(db.reference('Smartlight/lightstatus/light_1').get()))
		# db.reference('Smartlight/lightstatus/light_2').set("off")
