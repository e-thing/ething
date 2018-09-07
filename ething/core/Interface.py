# coding: utf-8

from .entity import Entity, path, abstract


@path('interfaces')
@abstract
class Interface (Entity):
    pass
