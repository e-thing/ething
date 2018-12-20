# coding: utf-8

from .switch import Switch
from ..reg import *


class Relay(Switch):

    @method.arg('state', type=Boolean())
    def setState(self, state):
        """
        set the current state of the switch
        """
        self.state = state

    @method
    def on(self):
        """
        turn on the switch
        """
        self.setState(state=True)

    @method
    def off(self):
        """
        turn off the switch
        """
        self.setState(state=False)

    @method
    def toggle(self):
        """
        toggle the switch
        """
        self.setState(not self.state)
