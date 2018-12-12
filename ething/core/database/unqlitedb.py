# coding: utf-8
from future.utils import binary_type
from .base import BaseClass
from ..TableQueryParser import TableQueryParser
from ..query import attribute_compiler
from ..Helpers import filter_obj
from ..env import USER_DIR
from ..ShortId import ShortId
from ..green import make_it_green
from unqlite import UnQLite
import os
import datetime
import sys
from dateutil import parser


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False


def decode_id(db_id):
    return str(db_id).zfill(7)


def encode_id(id):
    return int(id)


def decode_db(obj):
    if isinstance(obj, dict):
        if '__type' in obj:
            type = obj['__type'].decode('utf8')
            if type == 'datetime':
                return parser.parse(obj['value'].decode('utf8'))
            if type == 'unicode':
                return  obj['value'].decode('utf8')
            if type == 'binary':
                return  obj['value']
        else:
            for k in obj:
                obj[k] = decode_db(obj[k])
    elif isinstance(obj, binary_type):
        return obj.decode('utf8')
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = decode_db(obj[i])
    return obj


def encode_db(obj):
    if isinstance(obj, datetime.datetime):
        return {
            "__type": "datetime",
            "value": obj.isoformat()
        }

    if not py3:
        if isinstance(obj, unicode):
            return {
                "__type": "unicode",
                "value": obj.encode('utf8')
            }

    if py3:
        if isinstance(obj, binary_type):
            return {
                "__type": "binary",
                "value": obj
            }

    if isinstance(obj, dict):
        copy_obj = dict()
        for k in obj:
            copy_obj[k] = encode_db(obj[k])
        return copy_obj

    if isinstance(obj, list):
        copy_obj = list()
        for i in obj:
            copy_obj.append(encode_db(i))
        return copy_obj

    return obj


def decode(db_obj):
    del db_obj['__id']
    return decode_db(db_obj)


def encode(obj):
    return encode_db(obj)


class gUnQLite(UnQLite):
    """ A greenlet friendly sub-class of UnQLite. """

for method in [UnQLite.commit,
               UnQLite.commit_on_success,
               UnQLite.rollback]:
    setattr(gUnQLite, method.__name__, make_it_green(method))


class UnQLiteDB(BaseClass):

    def __init__(self, core, **config):
        super(UnQLiteDB, self).__init__(core, **config)
        if self.database == ':memory:':
            self.file = None
        else:
            self.file = os.path.join(USER_DIR, '%s.unqlite.db' % self.database)

    def connect(self):

        self.db = gUnQLite(self.file) if self.file else gUnQLite()

        self.log.info('connected to database: %s' % (self.file or 'memory'))

        #self.resources = self.db.collection('resources')
        self.fs = self.db.collection('fs')

        #self.resources.create()
        self.fs.create()

    def disconnect(self):
        if hasattr(self, 'db'):
            self.db.close()

    def get_usage(self):
        try:
            return os.path.getsize(self.file)
        except:
            return 0

    def clear(self):
        self.disconnect()
        if self.file:
            os.remove(self.file)
        self.connect()


    #
    # Resources
    #

    # def _get_db_id_from_resource_id(self, resource_id):
    #     rs = self.resources.filter(lambda r: decode_db(r['id']) == resource_id)
    #     if len(rs):
    #         return rs[0]['__id']
    #     raise Exception('unknown resource id "%s"' % resource_id)
    #
    # def list_resources(self):
    #     return map(decode, self.resources.all())
    #
    # def update_resource(self, resource):
    #     self.resources.update(self._get_db_id_from_resource_id(resource['id']), encode(resource))
    #     self.db.commit()
    #
    # def insert_resource(self, resource):
    #     self.resources.store(encode(resource))
    #     self.db.commit()
    #
    # def remove_resource(self, resource_id):
    #     self.resources.delete(self._get_db_id_from_resource_id(resource_id))
    #     self.db.commit()


    #
    # File System (used for storing images, text ...)
    #

    def _get_db_id_from_file_id(self, file_id):
        rs = self.fs.filter(lambda r: decode_db(r['id']) == file_id)
        if len(rs):
            return rs[0]['__id']
        raise Exception('unknown file id "%s"' % file_id)

    def storeFile(self, filename, contents, metadata=None):
        if contents:
            id = ShortId.generate()

            self.fs.store(encode({
                'id': id,
                'filename': filename,
                'metadata': metadata or {},
                'size': len(contents),
                'data': contents
            }))

            self.db.commit()

            return id

        return None

    def retrieveFile(self, file_id):
        content = None
        if file_id:
            record = self.fs.fetch(self._get_db_id_from_file_id(file_id))
            if record:
                return decode_db(record['data'])

        return content

    def removeFile(self, file_id):
        if file_id:
            self.fs.delete(self._get_db_id_from_file_id(file_id))
            self.db.commit()

    def getFileMetadata(self, file_id):
        metadata = {}

        if file_id:
            record = self.fs.fetch(self._get_db_id_from_file_id(file_id))
            if record:
                metadata = decode_db(record['metadata'])

        return metadata

    def getFileSize(self, file_id):
        if file_id:
            record = self.fs.fetch(self._get_db_id_from_file_id(file_id))
            if record:
                return record['size']

        return 0

    def listFiles(self):
        files = []
        for f in self.fs.all():
            f.pop('data', None)
            f = decode_db(f)
            files.append({
                'id': f['id'],
                'filename': f['filename'],
                'metadata': f['metadata'],
                'size': f['size']
            })


    #
    # Table (used for storing data time series)
    #

    def list_tables(self):
        if self.db.exists('collections'):
            collections = self.db['collections']
            if isinstance(collections, binary_type):
                collections = collections.decode('utf8')
            return collections.strip().split(' ')
        return []

    def create_table(self, table_name):
        table = self.db.collection(table_name)
        if not table.exists():
            table.create()
            self.db.append('collections', ' %s' % table_name)
            self.db.commit()

    def remove_table(self, table_name):
        table = self.db.collection(table_name)
        if table.exists():
            table.drop()
            collections = self.list_tables()
            collections.remove(table_name)
            self.db.store('collections', ' '.join(collections))
            self.db.commit()

    @make_it_green
    def get_table_rows(self, table_name, query = None, start=0, length=None, keys=None, sort=None):
        table = self.db.collection(table_name)
        rows = list(map(decode, table.all()))

        if query:
            parser = TableQueryParser(compiler=attribute_compiler, tz=getattr(self, 'tz', None))
            filter_fn = parser.compile(query)
            rows = [row for row in rows if filter_fn(row)]

        if sort:
            sort_attr = sort[0][0]
            asc = sort[0][1]
            rows = sorted(rows, key=lambda r: r.get(sort_attr, None), reverse=not asc)

            start = start or 0

        rows = rows[start:(length + start if length is not None else None)]
        
        if keys:
            rows = [filter_obj(row, keys) for row in rows]
        
        return rows

    def insert_table_row(self, table_name, row_data):
        table = self.db.collection(table_name)
        table.store(encode(row_data))
        self.db.commit()

    def update_table_row(self, table_name, row_id, row_data, return_old):
        """return the old row"""
        table = self.db.collection(table_name)

        rows = table.filter(lambda row: decode_db(row['id']) == row_id)
        updated_row = rows[0] if rows else None

        table.update(updated_row['__id'], encode(row_data))
        self.db.commit()

        if return_old:
            return decode(updated_row)

    def remove_table_row(self, table_name, row_id, return_old):
        """return the removed row"""
        table = self.db.collection(table_name)

        rows = table.filter(lambda row: decode_db(row['id']) == row_id)
        deleted_row = rows[0] if rows else None

        table.delete(deleted_row['__id'])
        self.db.commit()

        if return_old:
            return decode(deleted_row)

    def clear_table(self, table_name):
        table = self.db.collection(table_name)
        table.drop()
        table.create()
        self.db.commit()

