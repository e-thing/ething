# coding: utf-8

from .relay import Relay, interface, meta


@interface
@meta(icon='mdi-lightbulb-outline')
class Light (Relay):
    pass
