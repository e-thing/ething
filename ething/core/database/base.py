# coding: utf-8

from future.utils import integer_types
from ..ShortId import ShortId
import math
import logging


number_types = integer_types + (float, )

LOGGER = logging.getLogger('ething.db')


class BaseClass (object):

    def __init__(self, core, **config):
        self._core = core
        self.log = LOGGER

        for k in config:
            setattr(self, k, config[k])

    @property
    def core(self):
        return self._core

    def connect(self):
        raise NotImplementedError()

    def init(self):
        self._load_key_value_store()

    def disconnect(self):
        raise NotImplementedError()

    def get_usage(self):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()

    #
    # key/value
    #
    def _load_key_value_store(self):
        self._key_value_store_tablename = '_key_value_store'

        if not self.table_exists(self._key_value_store_tablename):
            self.create_table(self._key_value_store_tablename)

        rows = self.get_table_rows(self._key_value_store_tablename, length=1)
        if len(rows)==1:
            self._key_value_store_id = rows[0]['id']
            self._key_value_store_cache = rows[0]
        else:
            self._key_value_store_id = ShortId.generate()
            self._key_value_store_cache = {
                'id': self._key_value_store_id
            }
            self.insert_table_row(self._key_value_store_tablename, self._key_value_store_cache)

    def _update_key_value_store(self):
        self.update_table_row(self._key_value_store_tablename, self._key_value_store_id, self._key_value_store_cache, False)

    def kv_set(self, key, value):
        if key == 'id':
            raise Exception('invalid key')
        self._key_value_store_cache[key] = value
        self._update_key_value_store()

    def kv_get(self, key, default=None):
        return self._key_value_store_cache.get(key, default)

    def kv_remove(self, key):
        if key in self._key_value_store_cache:
            self._key_value_store_cache.pop(key)
            self._update_key_value_store()

    def kv_list(self):
        return [k for k in self._key_value_store_cache]

    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None):
        """return the file id"""
        raise NotImplementedError()

    def retrieveFile(self, file_id):
        raise NotImplementedError()

    def removeFile(self, file_id):
        raise NotImplementedError()

    def getFileMetadata(self, file_id):
        raise NotImplementedError()

    def getFileSize(self, file_id):
        raise NotImplementedError()

    def listFiles(self):
        raise NotImplementedError()


    #
    # Table (used for storing apikeys, time series ...)
    #
    def list_tables(self):
        raise NotImplementedError()

    def table_exists(self, table_name):
        return table_name in self.list_tables()

    def create_table(self, table_name):
        raise NotImplementedError()

    def remove_table(self, table_name):
        raise NotImplementedError()

    def get_table_rows(self, table_name, start=0, length=None, keys=None, sort=None):
        raise NotImplementedError()

    def get_table_row_by_id(self, table_name, row_id):
        raise NotImplementedError()

    def insert_table_row(self, table_name, row_data):
        raise NotImplementedError()

    def insert_table_rows(self, table_name, rows_data):
        for row_data in rows_data:
            self.insert_table_row(table_name, row_data)

    def update_table_row(self, table_name, row_id, row_data, return_old):
        """return the old row"""
        raise NotImplementedError()

    def remove_table_row(self, table_name, row_id, return_old):
        """return the removed row"""
        raise NotImplementedError()

    def remove_table_rows_by_id(self, table_name, row_ids, return_old):
        """return the removed rows"""
        removed_rows = []
        for row_id in row_ids:
            removed_row = self.remove_table_row(table_name, row_id, return_old=return_old)
            if removed_row:
                removed_rows.append(removed_row)
        if return_old:
            return removed_rows

    def clear_table(self, table_name):
        raise NotImplementedError()
