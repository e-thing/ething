# coding: utf-8

from ..Interface import Interface
from ..reg import *


@attr('state', type = Boolean(), default = False, mode = READ_ONLY, history = True, description = "the state of the switch")
class Switch(Interface):

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
