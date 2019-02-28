# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.core.interfaces import Button


class MihomeButton(MihomeDevice, Button):
    """
    Mihome button.
    """

    def processAttr(self, name, value):

        if name == 'status' or name == 'button_0':
            if value == 'click':
                self.click(type='single')
            elif value == 'long_click_release':
                self.click(type='long_click')
            elif value == 'double_click':
                self.click(type='double')

