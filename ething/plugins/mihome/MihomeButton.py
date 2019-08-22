# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.interfaces import Button


class MihomeButton(MihomeDevice, Button):
    """
    Mihome button.
    """

    @classmethod
    def isvalid(cls, gateway, model):
        return model in ['switch', 'sensor_switch', 'sensor_switch.aq2', 'sensor_switch.aq3', 'remote.b1acn01']

    def process_attr(self, name, value):

        if name == 'status' or name == 'button_0':
            if value == 'click':
                self.click(type='single')
            elif value == 'long_click_release':
                self.click(type='long_click')
            elif value == 'double_click':
                self.click(type='double')

