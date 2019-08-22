# coding: utf-8
from future.utils import string_types


from .YeelightDevice import YeelightDevice
from ething.interfaces import DimmableLight
from .yeelight import parse_brightness


class YeelightBulbMono (YeelightDevice, DimmableLight):

    def _update(self, params):

        super(YeelightBulbMono, self)._update(params)

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