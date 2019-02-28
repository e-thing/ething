# coding: utf-8

from .rgbLight import RGBLight
from .dimmable import Dimmable
from ..Interface import *


@interface
class RGBWLight (RGBLight, Dimmable):
    pass
