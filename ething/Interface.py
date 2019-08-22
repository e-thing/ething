# coding: utf-8

from .reg import *


def interface(cls):
    namespace('interfaces', inherit=False)(cls)
    abstract(cls)
    return cls
