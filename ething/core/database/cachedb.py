# coding: utf-8

from .base import BaseClass
from .cache import Db
from ..Helpers import filter_obj


class CacheDB(BaseClass):

    def __init__(self, core, driver, **config):
        super(CacheDB, self).__init__(core, **config)
        self._cachedb = Db(driver, auto_connect=False, auto_commit=config.get('auto_commit', False), cache_delay=config.get('cache_delay', 3600))
        self._fs = self._cachedb.fs

        if not self._cachedb.auto_commit:
            # commit every secondes
            self.core.scheduler.setInterval(config.get('commit_interval', 1), self.commit, condition=lambda _: self._cachedb.connected and self._cachedb.need_commit())

        # run garbage collector regularly
        self.core.scheduler.setInterval(300, self.run_garbage_collector, condition=lambda _: self._cachedb.connected)

    def connect(self):
        self._cachedb.connect()

    def disconnect(self):
        self._cachedb.disconnect()

    def get_usage(self):
        try:
            return self._cachedb.get_usage()
        except:
            return 0

    def clear(self):
        self._cachedb.clear()

    def commit(self):
        self._cachedb.commit()

    def run_garbage_collector(self):
        self._cachedb.run_garbage_collector()

    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None):
        """return the file id"""
        if metadata is None:
            metadata = dict()

        file = self._fs.create(filename, **metadata)
        file.write(contents)
        return file.id

    def retrieveFile(self, file_id):
        file = self._fs.get(file_id)
        return file.read()

    def removeFile(self, file_id):
        self._fs.remove(file_id)

    def getFileMetadata(self, file_id):
        file = self._fs.get(file_id)
        return file.metadata

    def getFileSize(self, file_id):
        file = self._fs.get(file_id)
        return file['size']

    def listFiles(self):
        return [{
            'id': f.id,
            'filename': f['filename'],
            'metadata': f.metadata,
            'size': f['size']
        } for f in self._fs.list()]


    #
    # Table (used for storing data time series)
    #

    def list_tables(self):
        return self._cachedb.list_tables()

    def create_table(self, table_name):
        self._cachedb.create(table_name)

    def remove_table(self, table_name):
        self._cachedb.drop(table_name)

    def get_table_row_by_id(self, table_name, row_id):
        table = self._cachedb[table_name]
        return table[row_id]

    def get_table_rows(self, table_name, start=0, length=None, keys=None, sort=None):

        table = self._cachedb[table_name]

        if sort:
            sort = sort[0]

        rows = table.select(sort=sort, start=start, length=length)

        if keys is not None:
            rows = [filter_obj(row, keys) for row in rows]

        return rows

    def insert_table_row(self, table_name, row_data):
        table = self._cachedb[table_name]
        table.insert(row_data)

    def update_table_row(self, table_name, row_id, row_data, return_old):
        """return the old row"""
        table = self._cachedb[table_name]
        old_doc = table.get_doc(row_id) if return_old else None
        table.update(row_data)
        return old_doc

    def remove_table_row(self, table_name, row_id, return_old):
        """return the removed row"""
        table = self._cachedb[table_name]
        deleted_row = table.get_doc(row_id) if return_old else None
        table.delete(row_id)
        return deleted_row

    def clear_table(self, table_name):
        table = self._cachedb[table_name]
        table.clear()

