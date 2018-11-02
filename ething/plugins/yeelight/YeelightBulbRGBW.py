# coding: utf-8
from future.utils import string_types


from .YeelightDevice import YeelightDevice
from ething.core.interfaces import RGBWLight
from .yeelight import parse_color, parse_brightness


class YeelightBulbRGBW (YeelightDevice, RGBWLight):

    def _update(self, params):

        super(YeelightBulbRGBW, self)._update(params)

        if 'color_mode' in params:
            self.color = parse_color(params)

        if 'bright' in params:
            self.level = parse_brightness(params)

    def setLevel(self, level):
        result = self.controller.send("set_bright", [level, "smooth", 100], done=lambda _, device: setattr(device, 'level', level))

        result.wait()

        if result.error:
            raise Exception(str(result.error))

    def setColor(self, color):
        color_int = int(color.replace('0x', '').replace('#', ''), 16)

        result = self.controller.send("set_rgb", [color_int, "smooth", 100], done=lambda _, device: setattr(device, 'color', color))

        result.wait()

        if result.error:
            raise Exception(str(result.error))