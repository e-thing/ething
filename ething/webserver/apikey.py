# coding: utf-8

from ething.core.dbentity import *
from ething.core.ShortId import ShortId, Id
from .Scope import ScopeType
import logging
import random
import datetime


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
@attr('modifiedDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Last time this API key was modified")
@attr('createdDate', default=lambda _: datetime.datetime.utcnow(), mode=READ_ONLY, description="Create time for this API key")
@attr('value', mode=READ_ONLY, default=lambda _: generate_apikey(), description="The API key")
@attr('name', type=String(allow_empty=False), description="The name of the API key")
@attr('id', default=lambda _: ShortId.generate(), mode=READ_ONLY, description="The id of the API key")
class Apikey(DbEntity):

    def __init__(self, data, create, manager):
        super(Apikey, self).__init__(data, create)
        object.__setattr__(self, '_Apikey__manager', manager)

    @property
    def manager(self):
        return self.__manager

    def __eq__(self, other):
        if isinstance(other, Apikey):
            return self.id == other.id
        else:
            return False

    def __str__(self):
        return 'Apikey(id=%s, name=%s)' % (self.id, self.name)

    def __repr__(self):
        return 'Apikey(id=%s, name=%s)' % (self.id, self.name)

    def __hash__(self):
        return hash(self.id)

    def _insert(self):
        self.manager.insert(self)
        self.manager.log.debug("apikey created : %s" % str(self))

    def _before_save(self):
        self._modifiedDate = datetime.datetime.utcnow()  # update the modification time

    def _save(self, dirty_attrs):
        self.manager.save(self)

    def _remove(self):
        self.manager.remove(self.id)
        self.manager.log.debug("apikey deleted : %s" % str(self))




class ApikeyManager(object):

    table_name = 'apikeys'

    def __init__(self, core):
        self.core = core
        self.db = core.db
        self.log = logging.getLogger('ething.apikeys')

        if not self.db.table_exists(self.table_name):
            self.db.create_table(self.table_name)

    def list(self):
        items = []
        for doc in self.db.get_table_rows(self.table_name):
            try:
                items.append(Apikey.unserialize(doc, manager=self))
            except:
                self.log.exception('invalid apikey document')
        return items

    def create(self, attributes):
        return Apikey.create(attributes, manager=self)

    def get(self, id):
        doc = self.db.get_table_row_by_id(self.table_name, id)
        if doc:
            return Apikey.unserialize(doc, manager=self)

    def find(self, key):
        rows = self.db.get_table_rows(self.table_name, query="value == '%s'" % key, length=1)
        if len(rows)>0:
            return Apikey.unserialize(rows[0], manager=self)

    def remove(self, id):
        self.db.remove_table_row(self.table_name, id)

    def insert(self, apikey):
        self.db.insert_table_row(self.table_name, apikey.serialize())

    def save(self, apikey):
        self.db.update_table_row(self.table_name, apikey.id, apikey.serialize())

    def clear(self):
        self.db.clear_table(self.table_name)