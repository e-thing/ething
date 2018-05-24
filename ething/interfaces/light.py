# coding: utf-8

from ething.meta import interface
from .switch import Switch


@interface
class Light (Switch):
    pass
