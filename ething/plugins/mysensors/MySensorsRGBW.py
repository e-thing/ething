# coding: utf-8

from .MySensorsSensor import MySensorsSensor
from ething.core.interfaces import RGBWLight
from .helpers import *
import colorsys


def hex_to_hsv(h):
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16)/255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(*rgb)


def hsv_to_hex(hue, sat, value):
    r, g, b = colorsys.hsv_to_rgb(hue, sat, value)
    return '#%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255))


class MySensorsRGBW (MySensorsSensor, RGBWLight):

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
        self.send(SET, V_STATUS, state, done = lambda _: setattr(self, 'state', state))

    def setColor(self, hue, saturation):

        def cb(d):
            with self:
                setattr(self, 'hue', hue)
                setattr(self, 'saturation', saturation)

        if sensorTypeInt(self.sensorType) == S_RGB_LIGHT:
            color = hsv_to_hex(hue / 360., saturation / 100., self.level / 100.)
            self.send(SET, V_RGB, color, done=cb)
        else:
            color = hsv_to_hex(hue / 360., saturation / 100., 1.)
            self.send(SET, V_RGBW, (color, self.level), done=cb)

    def setLevel(self, level):
        if sensorTypeInt(self.sensorType) == S_RGB_LIGHT:
            color = hsv_to_hex(self.hue / 360., self.saturation / 100., level / 100.)
            self.send(SET, V_RGB, color, done=lambda _: setattr(self, 'level', level))
        else:
            color = hsv_to_hex(self.hue / 360., self.saturation / 100., 1.)
            self.send(SET, V_RGBW, (color, level), done=lambda _: setattr(self, 'level', level))
