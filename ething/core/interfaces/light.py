# coding: utf-8

from .relay import Relay, interface


@interface
class Light (Relay):
    pass
