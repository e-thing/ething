# coding: utf-8
from ething.core.TransportProcess import BaseResult

specialCtrlCmds = ['OK', 'REBOOT', 'PING', 'PONG', 'VERSION', 'RFDEBUG', 'RFUDEBUG',
                   'QRFDEBUG', 'TRISTATEINVERT', 'RTSCLEAN', 'RTSRECCLEAN', 'RTSSHOW', 'RTSINVERT', 'RTSLONGTX']


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



def convertTemperature(value):
    value = int(value, 16)
    if value & 0x8000:
        # negative value
        value &= 0x7FFF
        value = -value

    value /= 10.
    return value


def convertBaro(value):
    return int(value, 16)


def convertHum(value):
    return int(value)


def convertUV(value):
    return int(value, 16)


def convertLux(value):
    return int(value, 16)


def convertRain(value):
    value = int(value, 16)
    value /= 10.
    return value  # in mm


def convertRainRate(value):
    value = int(value, 16)
    value /= 10.
    return value  # in mm/h


def convertWindSpeed(value):
    value = int(value, 16)
    value /= 10.
    return value  # in km. p/h


def convertWindGust(value):
    return int(value, 16)  # km. p/h


def convertWindDirection(value):
    value = int(value)
    return value * 22.5  # degrees


def convertWatt(value):
    return int(value, 16) / 10.  # watt


def convertKWatt(value):
    return convertWatt(value) * 1000.  # watt


def convertCurrent(value):
    return int(value, 16) / 10.  # A


def convertVoltage(value):
    return int(value, 16) / 10.  # V


def convertFreq(value):
    return int(value, 16)  # Hz


def convertPowerFactor(value):
    value = int(value, 16)
    if value & 0x8000:
        # negative value
        value &= 0x7FFF
        value = -value

    return value / 100.


def convertEnergy(value):
    return int(value, 16) / 10.  # units watt-hours


def convertForecast(value):
    if value == '1':
        return 'sunny'
    elif value == '2':
        return 'partly cloudy'
    elif value == '3':
        return 'cloudy'
    elif value == '4':
        return 'rain'

    return 'unknown'


def convertHygroStatus(value):
    if value == '0':
        return 'normal'
    elif value == '1':
        return 'confortable'
    elif value == '2':
        return 'dry'
    elif value == '3':
        return 'wet'

    return 'unknown'


def convertBattery(value):
    if value == 'OK':
        return 90
    elif value == 'LOW':
        return 10

    return None



attrMap = {
    'KWATT': ("watt", convertKWatt),
    'WATT': ("watt", convertWatt),
    'CURRENT': ("current", convertCurrent),
    'CURRENT2': ("current2", convertCurrent),
    'CURRENT3': ("current3", convertCurrent),
    'VOLT': ("voltage", convertVoltage),
    'FREQ': ("frequency", convertFreq),
    'PF': ("power factor", convertPowerFactor),
    'ENERGY': ("energy", convertEnergy),
    'TEMP': ("temperature", convertTemperature),
    'HUM': ("humidity", convertHum),
    'BARO': ("pressure", convertBaro),
    'UV': ("UV", convertUV),
    'RAIN': ("rain", convertRain),
    'RAINRATE': ("rain rate", convertRainRate),
    'WINSP': ("wind", convertWindSpeed),
    'AWINSP': ("average wind", convertWindSpeed),
    'WINGS': ("gust", convertWindGust),
    'WINDIR': ("wind direction", convertWindDirection),
    'WINCHL': ("wind chill", convertTemperature),  # wind chill
    # Wind meter temperature reading
    'WINTMP': ("wind temperature", convertTemperature),
    'LUX': ("lux", convertLux),
    # : (0=Normal, 1=Comfortable, 2=Dry, 3=Wet
    'HSTATUS': ("status", convertHygroStatus),
    # : (0=No Info/Unknown, 1=Sunny, 2=Partly Cloudy, 3=Cloudy, 4=Rain
    'BFORECAST': ("forecast", convertForecast),
}



def convertAttrValue(attr, value):
    return attrMap[attr][1](value) if attr in attrMap else value



# key: protocol, value: Data_Formatter instance
data_formatters = {}


class Data_Formatter(object):

    def write(self, protocol, **data):
        raise NotImplementedError()

    def parse(self, protocol, message):
        raise NotImplementedError()


class Default_Data_Formatter(Data_Formatter):

    def write(self, protocol, **data):
        return '%s;%s;%s;' % (data.get('ID', 0), data.get('SWITCH', 0), data.get('CMD'))

    def parse(self, protocol, message):
        items = message.split(';')
        data = {}

        for item in items:
            kv = item.split('=', 1)
            if len(kv) == 1:
                kv.append(True)
            data[kv[0]] = convertAttrValue(kv[0], kv[1])

        return data


default_data_formatter = Default_Data_Formatter()


def format_transmitted_data(protocol, **data):

    if protocol in data_formatters:
        formatter = data_formatters[protocol]
    else:
        formatter = default_data_formatter

    return '10;%s;%s' % (protocol, formatter.write(protocol, **data))

def parse_incoming_data(protocol, message):

    if protocol in data_formatters:
        formatter = data_formatters[protocol]
    else:
        formatter = default_data_formatter

    return formatter.parse(protocol, message)



def is_protocol(protocol):
    if '=' in protocol:
        return False
    if protocol == 'PONG':
        return False
    return True


class Result (BaseResult):
    def __init__(self, response, *args, **kwargs):
        super(Result, self).__init__(*args, **kwargs)
        self.response = response
