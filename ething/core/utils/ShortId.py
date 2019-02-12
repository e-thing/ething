# coding: utf-8
from future.utils import string_types


from shortid import ShortId as ShortIdlib
import re

from ..type import String


id_re = '^[-_a-zA-Z0-9]{7}$'

length = 7

alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'

sid = ShortIdlib()


def generate():
    return sid.generate()[-length:]


class Id(String):

    def __init__(self, **attributes):
        super(Id, self).__init__(regex=id_re, **attributes)

    def validate(self, value, context = None):
        try:
            return super(Id, self).validate(value, context)
        except ValueError:
            raise ValueError('not an id')
