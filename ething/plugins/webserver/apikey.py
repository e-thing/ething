# coding: utf-8

from ething.core.db import *
from ething.core.utils.date import TzDate, utcnow
from .Scope import ScopeType
import random


def generate_apikey():
    return '%04x%04x-%04x-%04x-%04x-%04x%04x%04x' % (
        # 32 bits for "time_low"
        random.randint(0, 0xffff), random.randint(0, 0xffff),
        # 16 bits for "time_mid"
        random.randint(0, 0xffff),
        # 16 bits for "time_hi_and_version",
        # four most significant bits holds version number 4
        random.randint(0, 0x0fff) | 0x4000,
        # 16 bits, 8 bits for "clk_seq_hi_res",
        # 8 bits for "clk_seq_low",
        # two most significant bits holds zero and one for variant DCE1.1
        random.randint(0, 0x3fff) | 0x8000,
        # 48 bits for "node"
        random.randint(0, 0xffff), random.randint(
            0, 0xffff), random.randint(0, 0xffff)
    )


@attr('scope', type=ScopeType(), default='', description="The scope for this API key")
@attr('modifiedDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Last time this API key was modified")
@attr('createdDate', type=TzDate(), default=lambda _: utcnow(), mode=READ_ONLY, description="Create time for this API key")
@attr('value', mode=READ_ONLY, default=lambda _: generate_apikey(), description="The API key")
@attr('name', type=String(allow_empty=False), description="The name of the API key")
@uid(description="The id of the API key")
@db(table='apikeys')
class Apikey(Entity):

    def __str__(self):
        return '<apikey id=%s name=%s>' % (self.id, self.name)

    def __repr__(self):
        return str(self)

    def __db_save__(self, insert):
        self.modifiedDate = utcnow()  # update the modification time

