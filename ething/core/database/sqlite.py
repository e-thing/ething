# coding: utf-8

from .base import BaseClass
from ..TableQueryParser import TableQueryParser
from ..query import attribute_compiler
from ..Helpers import filter_obj
from ..env import USER_DIR
from ..ShortId import ShortId
from ..green import make_it_green
from ..utils.lock import SecureLock
import sqlite3
import os
import json
import datetime
import time
import sys
from dateutil import parser
import threading


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False


class Cursor(sqlite3.Cursor):
    """ A greenlet friendly sub-class of sqlite3.Cursor. """


for method in [sqlite3.Cursor.executemany,
               sqlite3.Cursor.executescript,
               sqlite3.Cursor.fetchone,
               sqlite3.Cursor.fetchmany,
               sqlite3.Cursor.fetchall]:
    setattr(Cursor, method.__name__, make_it_green(method))

setattr(Cursor, 'execute', make_it_green(sqlite3.Cursor.execute))


class Connection(sqlite3.Connection):
    """ A greenlet friendly sub-class of sqlite3.Connection. """

    def __init__(self, *args, **kwargs):
        # by default [py]sqlite3 checks that object methods are run in the same
        # thread as the one that created the Connection or Cursor. If it finds
        # they are not then an exception is raised.
        # <https://docs.python.org/2/library/sqlite3.html#multithreading>
        # Luckily for us we can switch this check off.
        kwargs['check_same_thread'] = False
        super(Connection, self).__init__(*args, **kwargs)

    def cursor(self):
        return Cursor(self)

setattr(Connection, 'execute', make_it_green(sqlite3.Connection.execute))

for method in [sqlite3.Connection.commit,
               sqlite3.Connection.rollback]:
    setattr(Connection, method.__name__, make_it_green(method))


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        if py3 and isinstance(obj, bytes):
            return {
                "_type": "bytes",
                "value": obj.decode('utf8')
            }
        # Let the base class default method raise the TypeError
        return super(Encoder, self).default(obj)


class Decoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' in obj:
            type = obj['_type']
            if type == 'datetime':
                return parser.parse(obj['value'])
            if type == 'bytes':
                return obj['value'].encode('utf8')
        return obj

def to_timestamp(d):
    if d is not None:
        return time.mktime(d.timetuple())


class SQLite(BaseClass):

    def __init__(self, core, **config):
        super(SQLite, self).__init__(core, **config)
        if self.database == ':memory:':
            self.file = None
        else:
            self.file = os.path.join(USER_DIR, '%s.db' % self.database)
        self.lock = SecureLock(name='sqlite') # threading.Lock()

    def connect(self):
        with self.lock:
            self.db = sqlite3.connect(self.file or ':memory:', check_same_thread=False, factory=Connection)

            if self.db is None:
                raise Exception('unable to connect to the database')

            self.log.info('connected to database: %s' % (self.file or 'memory'))

            c = self.db.cursor()
            #c.execute('CREATE TABLE IF NOT EXISTS resources (id char(7), data json)')
            c.execute('CREATE TABLE IF NOT EXISTS fs (id char(7), filename text, size int, metadata text, content blob)')
            self.db.commit()
            c.close()

        self.upgrade()

    def upgrade(self):
        table_names = self.list_tables()

        for table_name in table_names:
            if table_name == 'fs':
                continue
            with self.lock:
                c = self.db.cursor()
                c.execute("SELECT sql FROM sqlite_master WHERE name='%s'" % table_name)
                sql_cmd = c.fetchone()[0]
                c.close()

            if ', date integer,' not in sql_cmd:
                self.log.warning('upgrading the table "%s"' % table_name)
                rows = self.get_table_rows(table_name)
                self.remove_table(table_name)
                self.create_table(table_name)
                self.insert_table_rows(table_name, rows)

    def disconnect(self):
        if hasattr(self, 'db'):
            with self.lock:
                self.db.commit()
                self.db.close()

    def get_usage(self):
        try:
            return os.path.getsize(self.file) if self.file else 0
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

    # def list_resources(self):
    #     with self.lock:
    #         resources = []
    #         c = self.db.cursor()
    #         for row in c.execute('SELECT data FROM resources'):
    #             resources.append(json.loads(row[0], cls=Decoder))
    #         c.close()
    #         return resources
    #
    # def update_resource(self, resource):
    #     with self.lock:
    #         c = self.db.cursor()
    #         c.execute(
    #             "UPDATE resources SET data = ? WHERE id = ?", (json.dumps(resource, cls=Encoder), resource['id']))
    #         self.db.commit()
    #         c.close()
    #
    # def insert_resource(self, resource):
    #     with self.lock:
    #         c = self.db.cursor()
    #         c.execute("INSERT INTO resources (id, data) VALUES (?, ?)", (resource['id'], json.dumps(resource, cls=Encoder)))
    #         self.db.commit()
    #         c.close()
    #
    # def remove_resource(self, resource_id):
    #     with self.lock:
    #         c = self.db.cursor()
    #         c.execute("DELETE FROM resources WHERE id = ?", (resource_id, ))
    #         self.db.commit()
    #         c.close()


    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None, id=None):
        if contents:
            with self.lock:
                id = ShortId.generate()
                c = self.db.cursor()
                c.execute("INSERT INTO fs (id, filename, size, metadata, content) VALUES (?, ?, ?, ?, ?)", (id, filename, len(contents), json.dumps(metadata or {}), sqlite3.Binary(contents)))
                self.db.commit()
                c.close()

            return id

        return None

    def retrieveFile(self, file_id):
        content = None
        if file_id:
            with self.lock:
                c = self.db.cursor()
                c.execute('SELECT content FROM fs WHERE id = ? LIMIT 1', (file_id, ))

                files = c.fetchall()
                if len(files) > 0:
                    content = files[0][0]
                    if not py3 and isinstance(content, buffer):
                        content = str(content) # convert buffer to string

                c.close()

        return content

    def removeFile(self, file_id):
        if file_id:
            with self.lock:
                c = self.db.cursor()
                c.execute("DELETE FROM fs WHERE id = ?", (file_id,))
                self.db.commit()
                c.close()

    def getFileMetadata(self, file_id):
        metadata = {}

        if file_id:
            with self.lock:
                c = self.db.cursor()
                c.execute('SELECT metadata FROM fs WHERE id = ? LIMIT 1', (file_id,))

                rows = c.fetchall()
                if len(rows) > 0:
                    metadata = json.loads(rows[0][0])

                c.close()

        return metadata

    def getFileSize(self, file_id):
        if file_id:
            with self.lock:
                c = self.db.cursor()
                c.execute('SELECT size FROM fs WHERE id = ? LIMIT 1', (file_id,))

                rows = c.fetchall()
                c.close()
                if len(rows) > 0:
                    return rows[0][0]

        return 0

    def listFiles(self):
        with self.lock:
            c = self.db.cursor()
            c.execute('SELECT id, filename, size, metadata FROM fs')
            files = c.fetchall()
            c.close()
            return [{
                'id': f[0],
                'filename': f[1],
                'metadata': json.loads(f[3]),
                'size': f[2]
            } for f in files]


    #
    # Table (used for storing data time series)
    #

    def list_tables(self):
        with self.lock:
            c = self.db.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            c.close()
            return [t[0] for t in tables]

    def create_table(self, table_name):
        with self.lock:
            c = self.db.cursor()
            c.execute("CREATE TABLE '%s' (id char(7), date integer, data json)" % (table_name,))
            self.db.commit()
            c.close()

    def remove_table(self, table_name):
        with self.lock:
            c = self.db.cursor()
            c.execute("DROP TABLE '%s'" % (table_name,))
            self.db.commit()
            c.close()

    def _select_table_rows_bulk(self, raw_rows, query = None, start=0, length=None, keys=None, sort=None):
        rows = [json.loads(row[0], cls=Decoder) for row in raw_rows]

        if query:
            parser = TableQueryParser(compiler=attribute_compiler, tz=getattr(self, 'tz', None))
            filter_fn = parser.compile(query)
            rows = [row for row in rows if filter_fn(row)]

        if sort:
            sort_attr = sort[0][0]
            asc = sort[0][1]
            rows = sorted(rows, key=lambda r: r.get(sort_attr, None), reverse=not asc)

        if start or length:
            start = start or 0
            rows = rows[start:(length + start if length is not None else None)]

        if keys is not None:
            rows = [filter_obj(row, keys) for row in rows]

        return rows

    _select_table_rows_green = make_it_green(_select_table_rows_bulk)

    def _select_table_rows(self, raw_rows, *args, **kwargs):
        if len(raw_rows) > 50:
            return self._select_table_rows_green(raw_rows, *args, **kwargs)
        else:
            return self._select_table_rows_bulk(raw_rows, *args, **kwargs)

    def get_table_rows(self, table_name, query = None, start=0, length=None, keys=None, sort=None):
        _rows = []

        if query is None:

            # do the sorting by SQL only if it is the date or id field
            sql_cmd = "SELECT data FROM '%s'" % (table_name,)
            fast = False

            if sort is not None:
                if len(sort) == 1:
                    sort_attr = sort[0][0]
                    if sort_attr == 'date' or sort_attr == 'id':
                        sql_cmd = sql_cmd + ' ORDER BY %s %s' % (sort_attr, 'ASC' if sort[0][1] else 'DESC')
                        fast = True
            else:
                fast = True

            if fast:
                has_limit = False
                if length is not None:
                    sql_cmd = sql_cmd + ' LIMIT %d' % length
                    has_limit = True

                if start>0:
                    if has_limit:
                        sql_cmd = sql_cmd + ' OFFSET %d' % start
                    else:
                        sql_cmd = sql_cmd + ' LIMIT 18446744 OFFSET %d' % start

                with self.lock:
                    c = self.db.cursor()
                    c.execute(sql_cmd)
                    _rows = c.fetchall()
                    c.close()

                return self._select_table_rows(_rows, None, None, None, keys, None)

        with self.lock:
            c = self.db.cursor()
            c.execute("SELECT data FROM '%s'" % (table_name,))
            _rows = c.fetchall()
            c.close()

        return self._select_table_rows(_rows, query, start, length, keys, sort)

    def insert_table_row(self, table_name, row_data):
        with self.lock:
            c = self.db.cursor()
            c.execute("INSERT INTO '%s' (id, date, data) VALUES (?, ?, ?)" % table_name, (row_data['id'], to_timestamp(row_data.get('date')), json.dumps(row_data, cls=Encoder)))
            self.db.commit()
            c.close()

    @make_it_green
    def _encode_table_rows(self, rows_data):
        _rows = []

        for row_data in rows_data:
            _rows.append((row_data['id'], to_timestamp(row_data.get('date')), json.dumps(row_data, cls=Encoder)))

        return _rows

    def insert_table_rows(self, table_name, rows_data):
        _rows = self._encode_table_rows(rows_data)

        with self.lock:
            c = self.db.cursor()
            c.executemany("INSERT INTO '%s' (id, date, data) VALUES (?, ?, ?)" % table_name, _rows)
            self.db.commit()
            c.close()

    def update_table_row(self, table_name, row_id, row_data, return_old):
        """return the old row"""
        with self.lock:
            c = self.db.cursor()

            if return_old:
                c.execute("SELECT data FROM '%s' WHERE id = ? LIMIT 1" % table_name, (row_id,))
                updated_row = c.fetchone()
                if updated_row:
                    updated_row = json.loads(updated_row[0], cls=Decoder)
            else:
                updated_row = None

            c.execute(
                "UPDATE '%s' SET data = ?, date = ? WHERE id = ?" % table_name,
                (json.dumps(row_data, cls=Encoder), to_timestamp(row_data.get('date')), row_id))

            self.db.commit()
            c.close()

            return updated_row

    def remove_table_row(self, table_name, row_id, return_old):
        """return the removed row"""
        with self.lock:
            c = self.db.cursor()

            if return_old:
                c.execute("SELECT data FROM '%s' WHERE id = ? LIMIT 1" % table_name, (row_id,))
                deleted_row = c.fetchone()
                if deleted_row:
                    deleted_row = json.loads(deleted_row[0], cls=Decoder)
            else:
                deleted_row = None

            c.execute("DELETE FROM '%s' WHERE id = ?" % table_name, (row_id,))

            self.db.commit()
            c.close()

            return deleted_row

    def clear_table(self, table_name):
        with self.lock:
            c = self.db.cursor()
            c.execute("DELETE FROM '%s'" % table_name)
            self.db.commit()
            c.close()

