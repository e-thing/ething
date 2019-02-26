# coding: utf-8

from .reg import *
from .Resource import Resource


@namespace('interfaces')
@abstract
class Interface (Resource):
    pass
