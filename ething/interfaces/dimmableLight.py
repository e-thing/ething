# coding: utf-8
from ething.meta import interface
from .dimmableSwitch import DimmableSwitch

@interface
class DimmableLight (DimmableSwitch):
    pass

