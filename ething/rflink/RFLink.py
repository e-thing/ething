





specialCtrlCmds = ['OK','REBOOT','PING','PONG','VERSION','RFDEBUG','RFUDEBUG','QRFDEBUG','TRISTATEINVERT','RTSCLEAN','RTSRECCLEAN','RTSSHOW','RTSINVERT','RTSLONGTX']


subTypes = [
	'switch',
	'light',
	'door',
	'motion',
	'thermometer',
	'weatherStation',
	'multimeter'
]

switchProtocols = [
	"X10",
	"Kaku",
	"AB400D",
	"Waveman",
	"EMW200",
	"Impuls",
	"RisingSun",
	"Philips",
	"Energenie",
	"Energenie5",
	"GDR2",
	"NewKaku",
	"HomeEasy",
	"Anslut",
	"Kambrook",
	"Ikea Koppla",
	"PT2262",
	"Lightwave",
	"EMW100",
	"BSB",
	"MDRemote",
	"Conrad",
	"Livolo",
	"TRC02RGB",
	"Aoke",
	"TRC022RGB",
	"Eurodomest",
	"Livolo App",
	"Blyss",
	"Byron",
	"Byron MP",
	"SelectPlus",
	"Doorbell",
	"FA20RF",
	"Chuango",
	"Plieger",
	"SilverCrest",
	"Mertik",
	"HomeConfort",
	"Powerfix",
	"TriState",
	"Deltronic",
	"FA500",
	"HT12E",
	"EV1527",
	"Elmes",
	"Aster",
	"Sartano",
	"Europe",
	"Avidsen",
	"BofuMotor",
	"BrelMotor",
	"RTS",
	"ElroDB",
	"Dooya",
	"Unitec",
	"Maclean",
	"R546",
	"Diya",
	"X10Secure",
	"Atlantic",
	"SilvercrestDB",
	"MedionDB",
	"VMC",
	"Keeloq",
	"CustomSwitch",
	"GeneralSwitch",
	"Koch",
	"Kingpin",
	"Funkbus",
	"Nice",
	"Forest",
	"MC145026",
	"Lobeco",
	"Friedland",
	"BFT",
	"Novatys",
	"Halemeier",
	"Gaposa",
	"MiLightv1",
	"MiLightv2",
	"HT6P20",
	"Doitrand",
	"Warema",
	"Ansluta",
	"Livcol",
	"Bosch",
	"Ningbo",
	"Ditec",
	"Steffen",
	"AlectoSA",
	"GPIOset",
	"KonigSec",
	"RM174RF",
	"Liwin",
	"YW_Secu",
	"Mertik_GV60",
	"Ningbo64",
	"X2D",
	"HRCMotor",
	"Velleman",
	"RFCustom",
	"YW_Sensor",
	"LEGRANDCAD",
	"SysfsGpio"
]


switchCmds = [
	"ON",
	"OFF",
	"ALLON",
	"ALLOFF",
	"DIM",
	"BRIGHT",
	"UP",
	"DOWN",
	"STOP",
	"COLOR",
	"DISCO+",
	"DISCO-"
]




def convertCmd (value):
	return  "on" in value.lower()



def convertTemperature (value):
	value = int(value, 16)
	if(value & 0x8000):
		# negative value
		value &= 0x7FFF
		value = -value
	
	value /= 10
	return value



def convertBaro (value):
	return int(value, 16)



def convertHum (value):
	return int(value)



def convertUV (value):
	return int(value, 16)



def convertLux (value):
	return int(value, 16)



def convertRain (value):
	value = int(value, 16)
	value /= 10
	return value # in mm



def convertRainRate (value):
	value = int(value, 16)
	value /= 10
	return value # in mm/h



def convertWindSpeed (value):
	value = int(value, 16)
	value /= 10
	return value # in km. p/h



def convertWindGust (value):
	return int(value, 16) # km. p/h



def convertWindDirection (value):
	value = int(value)
	return value * 22.5 # degrees 



def convertWatt (value):
	return int(value, 16) / 10 # watt



def convertKWatt (value):
	return convertWatt(value) * 1000 # watt



def convertCurrent (value):
	return int(value, 16) / 10 # A



def convertVoltage (value):
	return int(value, 16) / 10 # V



def convertFreq (value):
	return int(value, 16) # Hz



def convertPowerFactor (value):
	value = int(value, 16)
	if(value & 0x8000):
		# negative value
		value &= 0x7FFF
		value = -value
	
	return value / 100



def convertEnergy (value):
	return int(value, 16) / 10 # units watt-hours



def convertForecast (value):
	if value == '1':
		return 'sunny'
	elif value == '2':
		return 'partly cloudy'
	elif value == '3':
		return 'cloudy'
	elif value == '4':
		return 'rain'
	
	return 'unknown'



def convertHygroStatus (value):
	if value == '0':
		return 'normal'
	elif value == '1':
		return 'confortable'
	elif value == '2':
		return 'dry'
	elif value == '3':
		return 'wet'
	
	return 'unknown'



def convertBattery (value):
	if value == 'OK':
		return 90
	elif value == 'LOW':
		return 10
	
	return None


NO_STORE = 0
STORE = 1
STORE_SEPARATE = 2

attrMap = {
	'CMD' : ("state", convertCmd, STORE),
	'KWATT' : ("watt", convertKWatt, STORE),
	'WATT' : ("watt", convertWatt, STORE),
	'CURRENT' : ("current", convertCurrent, STORE),
	'CURRENT2' : ("current2", convertCurrent, STORE),
	'CURRENT3' : ("current3", convertCurrent, STORE),
	'VOLT' : ("voltage", convertVoltage, STORE),
	'FREQ' : ("frequency", convertFreq, STORE),
	'PF' : ("power factor", convertPowerFactor, STORE),
	'ENERGY' : ("energy", convertEnergy, STORE),
	'TEMP' : ("temperature", convertTemperature, STORE),
	'HUM' : ("humidity", convertHum, STORE),
	'BARO' : ("pressure", convertBaro, STORE),
	'UV' : ("UV", convertUV, STORE),
	'RAIN' : ("rain", convertRain, STORE),
	'RAINRATE' : ("rain rate", convertRainRate, STORE),
	'WINSP' : ("wind", convertWindSpeed, STORE),
	'AWINSP' : ("average wind", convertWindSpeed, STORE),
	'WINGS' : ("gust", convertWindGust, STORE),
	'WINDIR' : ("wind direction", convertWindDirection, STORE),
	'WINCHL' : ("wind chill", convertTemperature, STORE), # wind chill
	'WINTMP' : ("wind temperature", convertTemperature, STORE), # Wind meter temperature reading
	'LUX' : ("lux", convertLux, STORE),
	'HSTATUS' : ("status", convertHygroStatus, STORE), #  : (0=Normal, 1=Comfortable, 2=Dry, 3=Wet
	'BFORECAST' : ("forecast", convertForecast, STORE), # : (0=No Info/Unknown, 1=Sunny, 2=Partly Cloudy, 3=Cloudy, 4=Rain
	'BAT': ("battery", convertBattery, NO_STORE)
}


def getAttrName (attr):
	return attrMap[attr][0] if attr in attrMap else attr


def convertAttrValue (attr, value):
	return attrMap[attr][1](value) if attr in attrMap else value

def getSubType (protocol, args):
	
	if protocol == 'Debug' or not args:
		return
	
	# 20;83;Oregon Rain2;ID=2a19;RAIN=002a;RAINTOT=0054;BAT=OK
	if len([x for x in ['RAIN','RAINRATE','WINSP','AWINSP','WINGS','WINDIR','WINCHL','WINTMP','UV','LUX','HSTATUS','BFORECAST'] if x in args]) > 0:
		# generic Weather Station
		return 'weatherStation'
	
	
	# 20;1F;OregonV1;ID=000A;TEMP=00cd;BAT=LOW
	if 'ID' in args and 'TEMP' in args:
		# generic thermometer
		return 'thermometer'
	
	
	# 20;12;NewKaku;ID=000002;SWITCH=2;CMD=OFF
	if 'ID' in args and 'SWITCH' in args and 'CMD' in args and args['CMD'] in ['ON', 'OFF', 'ALLON', 'ALLOFF']:
		# generic switch
		return 'switch'
	
	
	if len([x for x in ['KWATT','WATT','CURRENT','CURRENT2','CURRENT3','VOLT','FREQ','PF','ENERGY'] if x in args]) > 0:
		# generic Weather Station
		return 'multimeter'
	
	
	return # unknow !



def convertSwitchId (value):
	# remove leading 0
	value = value.lstrip('0')
	if len(value)==0:
		value = '0'
	return value





