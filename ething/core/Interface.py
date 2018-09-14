# coding: utf-8

from .dbentity import DbEntity, path, abstract


@path('interfaces')
@abstract
class Interface (DbEntity):
    pass
