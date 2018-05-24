# coding: utf-8
from future.utils import string_types


from .YeelightDevice import YeelightDevice, method
from ething.Helpers import dict_recursive_update
from ething.interfaces import RGBWLight


class YeelightBulbRGBW (YeelightDevice, RGBWLight):

    def storeData(self, state):

        if 'rgb' in state:
            color = '#' + hex(state['rgb'])[2:].ljust(6, '0').upper()
            self.store('color', color, False)

        if 'bright' in state:
            self.store('level', state['bright'], False)

        super(YeelightBulbRGBW, self).storeData(state)

    # def getLevel(self):
    #    return self.getData('brightness', 0)

    def setLevel(self, level):
        self.sendMessage(
            '{"method":"set_bright", "params":[%d, "smooth", 100]}' % level)

    # def getColor(self):
    #    return self.getData('color', '#000000')

    def setColor(self, color):
        color = int(color.replace('0x', '').replace('#', ''), 16)
        self.sendMessage(
            '{"method":"set_rgb", "params":[%d, "smooth", 100]}' % color)

    # @method.return_type('number')
    # def getBrightness(self):
    #    """
    #    return the brightness (%).
    #    """
    #    return self.getData('brightness', 0)
    #
    # @method.return_type('string')
    # def getColor(self):
    #    """
    #    return the color (hex).
    #    """
    #    return self.getData('color', '#000000')
    #
    # @method.arg('temperature', type="integer")
    # @method.arg('brightness', type="integer", minimum=0, maximum=100)
    # def setTemperature(self, temperature, brightness = 100):
    #    """
    #    turn on the device with the specified temperature.
    #    """
    #    return self.sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["ct", %d, %d]}' % (temperature,brightness))
    #
    # @method.arg('color', type="string", description="It should be expressed in hexadecimal, by exemple 0xFFFFFF).")
    # @method.arg('brightness', type="integer", minimum=0, maximum=100)
    # def setColor(self, color, brightness = 100):
    #    """
    #    turn on the device with the specified color.
    #    """
    #    if isinstance(color, string_types):
    #        color = int(color.replace('0x','').replace('#',''), 16)
    #
    #    return self.sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["color", %d, %d]}' % (color,brightness))
    #
    # @method.arg('hue', type="integer", minimum=0, maximum=359)
    # @method.arg('saturation', type="integer", minimum=0, maximum=100)
    # @method.arg('brightness', type="integer", minimum=0, maximum=100)
    # def setHSV(self, hue, saturation, brightness = 100):
    #    """
    #    turn on the device with the specified hsv set.
    #    """
    #    return self.sendMessageWaitResponse('{"id":1,"method":"set_scene", "params":["hsv", %d, %d, %d]}' % (hue,saturation,brightness))
    #
