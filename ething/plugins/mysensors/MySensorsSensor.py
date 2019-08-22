# coding: utf-8

from ething.Device import Device
from ething.reg import *
from .helpers import *


@abstract
@attr('name', default='sensor')
@attr('sensorId', type=Integer(min=0, max=254), description="The id of the sensor.")
@attr('sensorType', mode = READ_ONLY, description="The type of the sensor.")
@attr('createdBy', required=True)
class MySensorsSensor (with_metaclass(MySensorsSensorMetaClass, Device)):
    """
    MySensorsSensor Device resource representation. This device is normally automatically created by a MySensorsNode instance.
    """

    @property
    def node(self):
        return self.createdBy

    @property
    def nodeId(self):
        return self.node.nodeId

    @property
    def gateway(self):
        return self.node.gateway

    @property
    def controller(self):
        return self.gateway.controller

    def send(self, type, subtype, payload=None, **kwargs):
        """
        send a message.
        """
        return self.node.send(self.sensorId, type, subtype, payload, **kwargs)

    def _set_data(self, datatype, value):
        """
        :param datatype: type of data as an integer
        :param value: formatted value according to valueTypes
        """
        pass

    def _get_data(self, datatype):
        """
        :param datatype: type of data as an integer
        :return: the value of the data
        """
        pass


from ething.interfaces import *
from ething.interfaces.sensor import *


# S_DOOR;0;Door and window sensors;V_TRIPPED, V_ARMED

@attr('name', default='Door sensor')
class MySensorsDoor (MySensorsSensor, DoorSensor):
    S = S_DOOR

    def _set_data(self, datatype, value):
        if datatype == V_TRIPPED:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_TRIPPED:
            return self.state

# S_MOTION;1;Motion sensors;V_TRIPPED, V_ARMED

@attr('name', default='Motion sensor')
class MySensorsMotion (MySensorsSensor, OccupencySensor):
    S = S_MOTION

    def _set_data(self, datatype, value):
        if datatype == V_TRIPPED:
            self.presence = value

    def _get_data(self, datatype):
        if datatype == V_TRIPPED:
            return self.presence

# S_SMOKE;2;Smoke sensor;V_TRIPPED, V_ARMED

@attr('name', default='Smoke sensor')
class MySensorsSmoke (MySensorsSensor, BinarySensor):
    S = S_SMOKE

    def _set_data(self, datatype, value):
        if datatype == V_TRIPPED:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_TRIPPED:
            return self.state

# S_BINARY;3;Binary device (on/off);V_STATUS, V_WATT

@attr('name', default='binary device')
class MySensorsBinary (MySensorsSensor, Relay):
    S = S_BINARY

    def _set_data(self, datatype, value):
        if datatype == V_STATUS or datatype == V_LIGHT:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_STATUS or datatype == V_LIGHT:
            return self.state

    def setState(self, state):
        self.send(SET, V_STATUS, value=state, done = lambda _: setattr(self, 'state', state))

# S_DIMMER;4;Dimmable device of some kind;V_STATUS (on/off), V_PERCENTAGE (dimmer level 0-100), V_WATT

@attr('name', default='dimmer')
class MySensorsDimmer (MySensorsSensor, DimmableRelay):
    S = S_DIMMER

    def _set_data(self, datatype, value):
        if datatype == V_PERCENTAGE or datatype == V_DIMMER:
            self.level = value
        elif datatype == V_STATUS or datatype == V_LIGHT:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_PERCENTAGE or datatype == V_DIMMER:
            return self.level
        elif datatype == V_STATUS or datatype == V_LIGHT:
            return self.state

    def setState(self, state):
        self.send(SET, V_STATUS, value=state, done = lambda _: setattr(self, 'state', state))

    def setLevel(self, level):
        self.send(SET, V_PERCENTAGE, value=level, done=lambda _: setattr(self, 'level', level))


# S_COVER;5;Window covers or shades;V_UP, V_DOWN, V_STOP, V_PERCENTAGE
# todo

# S_TEMP;6;Temperature sensor;V_TEMP, V_ID

@attr('name', default='thermometer')
class MySensorsTemp (MySensorsSensor, Thermometer):
    S = S_TEMP

    def _set_data(self, datatype, value):
        if datatype == V_TEMP:
            self.temperature = value

    def _get_data(self, datatype):
        if datatype == V_TEMP:
            return self.temperature

# S_HUM;7;Humidity sensor;V_HUM

@attr('name', default='Humidity sensor')
class MySensorsHum (MySensorsSensor, HumiditySensor):
    S = S_HUM

    def _set_data(self, datatype, value):
        if datatype == V_HUM:
            self.humidity = value

    def _get_data(self, datatype):
        if datatype == V_HUM:
            return self.humidity

# S_BARO;8;Barometer sensor (Pressure);V_PRESSURE, V_FORECAST

@attr('name', default='Barometer')
class MySensorsBaro (MySensorsSensor, PressureSensor):
    S = S_BARO

    def _set_data(self, datatype, value):
        if datatype == V_PRESSURE:
            self.pressure = value

    def _get_data(self, datatype):
        if datatype == V_PRESSURE:
            return self.pressure

# S_WIND;9;Wind sensor;V_WIND, V_GUST, V_DIRECTION

@attr('name', default='Wind sensor')
class MySensorsWind(MySensorsSensor, PressureSensor):
    S = S_WIND

    def _set_data(self, datatype, value):
        if datatype == V_WIND:
            self.wind_speed = value
        elif datatype == V_DIRECTION:
            self.wind_direction = value

    def _get_data(self, datatype):
        if datatype == V_WIND:
            return self.wind_speed
        elif datatype == V_DIRECTION:
            return self.wind_direction

# S_RAIN;10;Rain sensor;V_RAIN, V_RAINRATE

@attr('name', default='Rain sensor')
class MySensorsRain(MySensorsSensor, GenericSensor):
    S = S_RAIN

    def _set_data(self, datatype, value):
        if datatype == V_RAIN:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_RAIN:
            return self.value

# S_UV;11;UV sensor;V_UV

@attr('name', default='UV sensor')
class MySensorsUV(MySensorsSensor, GenericSensor):
    S = S_UV

    def _set_data(self, datatype, value):
        if datatype == V_UV:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_UV:
            return self.value

# S_WEIGHT;12;Weight sensor for scales etc.;V_WEIGHT, V_IMPEDANCE

@attr('name', default='Weight sensor')
class MySensorsWeight(MySensorsSensor, GenericSensor):
    S = S_WEIGHT

    def _set_data(self, datatype, value):
        if datatype == V_WEIGHT:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_WEIGHT:
            return self.value

# S_POWER;13;Power measuring device, like power meters;V_WATT, V_KWH, V_VAR, V_VA, V_POWER_FACTOR

@attr('name', default='Power meters')
class MySensorsPower(MySensorsSensor, PowerMeter):
    S = S_POWER

    def _set_data(self, datatype, value):
        if datatype == V_WATT:
            self.power = value

    def _get_data(self, datatype):
        if datatype == V_WATT:
            return self.power

# S_HEATER;14;Heater device;V_HVAC_SETPOINT_HEAT, V_HVAC_FLOW_STATE, V_TEMP, V_STATUS
# todo

# S_DISTANCE;15;Distance sensor;V_DISTANCE, V_UNIT_PREFIX

@attr('name', default='Distance sensor')
class MySensorsDistance(MySensorsSensor, GenericSensor):
    S = S_DISTANCE

    def _set_data(self, datatype, value):
        if datatype == V_DISTANCE:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_DISTANCE:
            return self.value

# S_LIGHT_LEVEL;16;Light sensor;V_LIGHT_LEVEL (uncalibrated percentage), V_LEVEL (light level in lux)

@attr('name', default='Light sensor')
class MySensorsLightLevel(MySensorsSensor, LightSensor):
    S = S_LIGHT_LEVEL

    def _set_data(self, datatype, value):
        if datatype == V_LIGHT_LEVEL or datatype == V_LEVEL:
            self.light_level = value

    def _get_data(self, datatype):
        if datatype == V_LIGHT_LEVEL or datatype == V_LEVEL:
            return self.light_level

# S_ARDUINO_NODE;17;Arduino node device
# todo

# S_ARDUINO_REPEATER_NODE;18;Arduino repeating node device
# todo

# S_LOCK;19;Lock device;V_LOCK_STATUS

@attr('name', default='Lock device')
class MySensorsLock (MySensorsSensor, BinarySensor):
    S = S_LOCK

    def _set_data(self, datatype, value):
        if datatype == V_LOCK_STATUS:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_LOCK_STATUS:
            return self.state

# S_IR;20;Ir sender/receiver device;V_IR_SEND, V_IR_RECEIVE, V_IR_RECORD
# todo

# S_WATER;21;Water meter;V_FLOW, V_VOLUME

@attr('name', default='Water meter')
@sensor_attr('flow', type = Number(), default = 0)
@sensor_attr('volume', type = Number(), default = 0)
class MySensorsWater(MySensorsSensor, Sensor):
    S = S_WATER

    def _set_data(self, datatype, value):
        if datatype == V_FLOW:
            self.flow = value
        elif datatype == V_VOLUME:
            self.volume = value

    def _get_data(self, datatype):
        if datatype == V_VOLUME:
            return self.flow
        elif datatype == V_VOLUME:
            return self.volume

# S_AIR_QUALITY;22;Air quality sensor e.g. MQ-2;V_LEVEL, V_UNIT_PREFIX

@attr('name', default='Air quality sensor')
class MySensorsAirQuality(MySensorsSensor, GenericSensor):
    S = S_AIR_QUALITY

    def _set_data(self, datatype, value):
        if datatype == V_LEVEL:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_LEVEL:
            return self.value

# S_CUSTOM;23;Use this for custom sensors where no other fits.
# todo

# S_DUST;24;Dust level sensor;V_LEVEL, V_UNIT_PREFIX

@attr('name', default='Dust level sensor')
class MySensorsDust(MySensorsSensor, GenericSensor):
    S = S_DUST

    def _set_data(self, datatype, value):
        if datatype == V_LEVEL:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_LEVEL:
            return self.value

# S_SCENE_CONTROLLER;25;Scene controller device;V_SCENE_ON, V_SCENE_OFF
# todo

# S_RGB_LIGHT;26;RGB light;V_RGB, V_WATT
# S_RGBW_LIGHT;27;RGBW light (with separate white component);V_RGBW, V_WATT

import colorsys


def hex_to_hsv(h):
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(*rgb)


def hsv_to_hex(hue, sat, value):
    r, g, b = colorsys.hsv_to_rgb(hue, sat, value)
    return '#%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255))


class MySensorsRGBW (MySensorsSensor, RGBWLight):
    S = [S_RGB_LIGHT, S_RGBW_LIGHT]

    def _set_data(self, datatype, value):
        super(MySensorsRGBW, self)._set_data(datatype, value)
        if datatype == V_RGB: # value = #FF0000
            hue, sat, brightness = hex_to_hsv(value)
            self.hue = hue * 360.
            self.saturation = sat * 100.
            self.level = brightness * 100.
        elif datatype == V_RGBW: # value = #FF0000FF
            color, level = value
            hue, sat, _ = hex_to_hsv(color)
            self.hue = hue * 360.
            self.saturation = sat * 100.
            self.level = level
        elif datatype == V_STATUS:
            self.state = value
        elif datatype == V_PERCENTAGE or datatype == V_DIMMER:
            self.level = value

    def setState(self, state):
        self.send(SET, V_STATUS, value=state, done = lambda _: setattr(self, 'state', state))

    def setColor(self, hue, saturation):

        def cb(d):
            with self:
                setattr(self, 'hue', hue)
                setattr(self, 'saturation', saturation)

        if sensorTypeInt(self.sensorType) == S_RGB_LIGHT:
            color = hsv_to_hex(hue / 360., saturation / 100., self.level / 100.)
            self.send(SET, V_RGB, value=color, done=cb)
        else:
            color = hsv_to_hex(hue / 360., saturation / 100., 1.)
            self.send(SET, V_RGBW, value=(color, self.level), done=cb)

    def setLevel(self, level):
        if sensorTypeInt(self.sensorType) == S_RGB_LIGHT:
            color = hsv_to_hex(self.hue / 360., self.saturation / 100., level / 100.)
            self.send(SET, V_RGB, value=color, done=lambda _: setattr(self, 'level', level))
        else:
            color = hsv_to_hex(self.hue / 360., self.saturation / 100., 1.)
            self.send(SET, V_RGBW, value=(color, level), done=lambda _: setattr(self, 'level', level))


# S_COLOR_SENSOR;28;Color sensor;V_RGB

@attr('name', default='Color sensor')
class MySensorsColorSensor(MySensorsSensor, GenericSensor):
    S = S_COLOR_SENSOR

    def _set_data(self, datatype, value):
        if datatype == V_RGB:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_RGB:
            return self.value

# S_HVAC;29;Thermostat/HVAC device;V_STATUS, V_TEMP, V_HVAC_SETPOINT_HEAT, V_HVAC_SETPOINT_COOL, V_HVAC_FLOW_STATE, V_HVAC_FLOW_MODE, V_HVAC_SPEED
# todo

# S_MULTIMETER;30;Multimeter device;V_VOLTAGE, V_CURRENT, V_IMPEDANCE

@attr('name', default='Water meter')
@sensor_attr('voltage', type = Number(), default = 0)
@sensor_attr('current', type = Number(), default = 0)
@sensor_attr('impedance', type = Number(), default = 0)
class MySensorsMultimeter(MySensorsSensor, Sensor):
    S = S_MULTIMETER

    def _set_data(self, datatype, value):
        if datatype == V_VOLTAGE:
            self.voltage = value
        elif datatype == V_CURRENT:
            self.current = value
        elif datatype == V_IMPEDANCE:
            self.impedance = value

    def _get_data(self, datatype):
        if datatype == V_VOLTAGE:
            return self.voltage
        elif datatype == V_CURRENT:
            return self.current
        elif datatype == V_IMPEDANCE:
            return self.impedance

# S_SPRINKLER;31;Sprinkler device;V_STATUS (turn on/off), V_TRIPPED (if fire detecting device)

@attr('name', default='Sprinkler')
class MySensorsSprinkler (MySensorsSensor, Relay):
    S = S_SPRINKLER

    def _set_data(self, datatype, value):
        if datatype == V_STATUS:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_STATUS:
            return self.state

    def setState(self, state):
        self.send(SET, V_STATUS, value=state, done = lambda _: setattr(self, 'state', state))

# S_WATER_LEAK;32;Water leak sensor;V_TRIPPED, V_ARMED

@attr('name', default='Water leak sensor')
class MySensorsWaterLeak (MySensorsSensor, BinarySensor):
    S = S_WATER_LEAK

    def _set_data(self, datatype, value):
        if datatype == V_TRIPPED:
            self.state = value

    def _get_data(self, datatype):
        if datatype == V_TRIPPED:
            return self.state

# S_SOUND;33;Sound sensor;V_LEVEL (in dB), V_TRIPPED, V_ARMED

@attr('name', default='Sound sensor')
class MySensorsSound(MySensorsSensor, GenericSensor):
    S = S_SOUND

    def _set_data(self, datatype, value):
        if datatype == V_LEVEL:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_LEVEL:
            return self.value

# S_VIBRATION;34;Vibration sensor;V_LEVEL (vibration in Hz), V_TRIPPED, V_ARMED

@attr('name', default='Vibration sensor')
class MySensorsVibration(MySensorsSensor, GenericSensor):
    S = S_VIBRATION

    def _set_data(self, datatype, value):
        if datatype == V_LEVEL:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_LEVEL:
            return self.value

# S_MOISTURE;35;Moisture sensor;V_LEVEL (water content or moisture in percentage?), V_TRIPPED, V_ARMED

@attr('name', default='Moisture sensor')
class MySensorsMoisture(MySensorsSensor, MoistureSensor):
    S = S_MOISTURE

    def _set_data(self, datatype, value):
        if datatype == V_LEVEL:
            self.moisture = value

    def _get_data(self, datatype):
        if datatype == V_LEVEL:
            return self.moisture

# S_INFO;36;LCD text device;V_TEXT
# todo

# S_GAS;37;Gas meter;V_FLOW, V_VOLUME

@attr('name', default='Gas meter')
@sensor_attr('flow', type = Number(), default = 0)
@sensor_attr('volume', type = Number(), default = 0)
class MySensorsGas(MySensorsSensor, Sensor):
    S = S_WATER

    def _set_data(self, datatype, value):
        if datatype == V_FLOW:
            self.flow = value
        elif datatype == V_VOLUME:
            self.volume = value

    def _get_data(self, datatype):
        if datatype == V_VOLUME:
            return self.flow
        elif datatype == V_VOLUME:
            return self.volume

# S_GPS;38;GPS Sensor;V_POSITION

@attr('name', default='GPS sensor')
class MySensorsGPS(MySensorsSensor, GenericSensor):
    S = S_GPS

    def _set_data(self, datatype, value):
        if datatype == V_POSITION:
            self.value = value

    def _get_data(self, datatype):
        if datatype == V_POSITION:
            return self.value

# S_WATER_QUALITY;39;Water quality sensor;V_TEMP, V_PH, V_ORP, V_EC, V_STATUS

@attr('name', default='Water quality sensor')
@sensor_attr('ph', type = Number(), default = 0)
@sensor_attr('orp', type = Number(), default = 0)
@sensor_attr('ec', type = Number(), default = 0)
class MySensorsWaterQuality(MySensorsSensor, Thermometer):
    S = S_WATER_QUALITY

    def _set_data(self, datatype, value):
        if datatype == V_TEMP:
            self.temperature = value
        elif datatype == V_PH:
            self.ph = value
        elif datatype == V_ORP:
            self.orp = value
        elif datatype == V_EC:
            self.ec = value

    def _get_data(self, datatype):
        if datatype == V_TEMP:
            return self.temperature
        elif datatype == V_PH:
            return self.ph
        elif datatype == V_ORP:
            return self.orp
        elif datatype == V_EC:
            return self.ec



