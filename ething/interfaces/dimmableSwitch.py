# coding: utf-8

from .switch import Switch
from .dimmable import Dimmable


class DimmableSwitch(Switch, Dimmable):
    pass
