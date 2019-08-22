# coding: utf-8
from future.utils import string_types


from .YeelightDevice import YeelightDevice
from ething.interfaces import RGBWLight
from .yeelight import parse_color, parse_brightness
import colorsys


class YeelightBulbRGBW (YeelightDevice, RGBWLight):

    def _update(self, params):

        super(YeelightBulbRGBW, self)._update(params)

        if 'color_mode' in params:
            hue, saturation = parse_color(params)
            self.hue = hue
            self.saturation = saturation

        if 'bright' in params:
            self.level = parse_brightness(params)

    def setState(self, state):
        result = self.controller.send("set_power", ["on" if state else "off", "smooth", 100], done=lambda _, device: setattr(device, 'state', state))

        result.wait()

        if result.error:
            raise Exception(str(result.error))

    def setLevel(self, level):
        result = self.controller.send("set_bright", [level, "smooth", 100], done=lambda _, device: setattr(device, 'level', level))

        result.wait()

        if result.error:
            raise Exception(str(result.error))

    def setColor(self, hue, saturation):

        if 'set_hsv' in self._support:
            result = self.controller.send("set_rgb", [hue, saturation, "smooth", 100], done=lambda _, device: super(YeelightBulbRGBW, self).setColor(hue, saturation))
        else:
            r, g, b = colorsys.hsv_to_rgb(hue / 360., saturation / 100., self.level / 100.)
            color_int = int('%02X%02X%02X' % (int(r * 255), int(g * 255), int(b * 255)), 16)
            result = self.controller.send("set_rgb", [color_int, "smooth", 100], done=lambda _, device: super(YeelightBulbRGBW, self).setColor(hue, saturation))

        result.wait()

        if result.error:
            raise Exception(str(result.error))