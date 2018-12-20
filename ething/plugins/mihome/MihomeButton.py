# coding: utf-8


from .MihomeDevice import MihomeDevice
from ething.core.interfaces.button import Button, ButtonClicked


class MihomeButton(MihomeDevice, Button):
    """
    Mihome button.
    """

    def processAttr(self, name, value):

        if name == 'status' or name == 'button_0':
            if value == 'click':
                self.dispatchSignal(ButtonClicked(self, type='single'))
            elif value == 'long_click_release':
                self.dispatchSignal(ButtonClicked(self, type='long_click'))
            elif value == 'double_click':
                self.dispatchSignal(ButtonClicked(self, type='double'))

