# coding: utf-8
from future.utils import string_types


from shortid import ShortId as ShortIdlib
import re

from .type import String


id_re = '^[-_a-zA-Z0-9]{7}$'

class ShortId(object):

    sid = None

    # length of the identifier (must be between 7 and 14)
    length = 7
    # alphabet to use when generating the identifier (must be 64 characters long)
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-'

    @staticmethod
    def generate():

        if ShortId.sid is None:
            ShortId.sid = ShortIdlib()

        return ShortId.sid.generate()[:ShortId.length]

    @staticmethod
    def validate(id):
        if isinstance(id, string_types) and len(id) == ShortId.length:
            match = re.match("^["+ShortId.alphabet+"]*$", id)
            return match is not None
        return False


class Id(String):

    def __init__(self, **attributes):
        super(Id, self).__init__(regex=id_re, **attributes)

    def validate(self, value):
        try:
            return super(Id, self).validate(value)
        except ValueError:
            raise ValueError('not an id')
