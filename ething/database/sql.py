# coding: utf-8

from .base import BaseClass
from ething.TableQueryParser import TableQueryParser
from ething.query import attribute_compiler
from ething.Helpers import filter_obj
from ething.env import USER_DIR
from ething.ShortId import ShortId
import sqlite3
import os
import json
import datetime
from dateutil import parser


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        # Let the base class default method raise the TypeError
        return super(Encoder, self).default(obj)


class Decoder(json.JSONDecoder):

    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        type = obj['_type']
        if type == 'datetime':
            return parser.parse(obj['value'])
        return obj


class SQL(BaseClass):

    def __init__(self, **config):
        super(SQL, self).__init__(**config)
        self.file = os.path.join(USER_DIR, '%s.db' % self.database)

    def connect(self):

        self.db = sqlite3.connect(self.file)

        if self.db is None:
            raise Exception('unable to connect to the database')

        self.log.info('connected to database: %s' % self.file)

        c = self.db.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS resources (id char(7), data text)')
        c.execute('CREATE TABLE IF NOT EXISTS fs (id char(7), filename text, size int, metadata text, content blob)')
        self.db.commit()
        c.close()


    def disconnect(self):
        if hasattr(self, 'db'):
            self.db.commit()
            self.db.close()

    def get_usage(self):
        try:
            return os.path.getsize(self.file)
        except:
            return 0

    def clear(self):
        self.disconnect()
        os.remove(self.file)
        self.connect()


    #
    # Resources
    #

    def list_resources(self):
        resources = []
        c = self.db.cursor()
        for row in c.execute('SELECT data FROM resources'):
            resources.append(json.loads(row[0], cls=Decoder))
        c.close()
        return resources

    def update_resource(self, resource):
        c = self.db.cursor()
        c.execute(
            "UPDATE resources SET data = ? WHERE id = ?", (json.dumps(resource, cls=Encoder), resource['id']))
        self.db.commit()
        c.close()

    def insert_resource(self, resource):
        c = self.db.cursor()
        c.execute("INSERT INTO resources (id, data) VALUES (?, ?)", (resource['id'], json.dumps(resource, cls=Encoder)))
        self.db.commit()
        c.close()

    def remove_resource(self, resource_id):
        c = self.db.cursor()
        c.execute("DELETE FROM resources WHERE id = ?", (resource_id, ))
        self.db.commit()
        c.close()


    #
    # File System (used for storing images, text ...)
    #

    def storeFile(self, filename, contents, metadata=None):
        if contents:
            id = ShortId.generate()
            c = self.db.cursor()
            c.execute("INSERT INTO fs (id, filename, size, metadata, content) VALUES (?, ?, ?, ?, ?)", (id, filename, len(contents), json.dumps(metadata), sqlite3.Binary(contents)))
            file_id = c.lastrowid
            self.db.commit()
            c.close()

            return id

        return None

    def retrieveFile(self, file_id):
        content = None
        if file_id:

            c = self.db.cursor()
            c.execute('SELECT content FROM fs WHERE id = ?', (file_id, ))

            files = c.fetchall()
            if len(files) > 0:
                content = str(files[0][0])

            c.close()

        return content

    def removeFile(self, file_id):
        if file_id:
            c = self.db.cursor()
            c.execute("DELETE FROM fs WHERE id = ?", (file_id,))
            self.db.commit()
            c.close()

    def getFileMetadata(self, file_id):
        metadata = {}

        if file_id:
            c = self.db.cursor()
            c.execute('SELECT metadata FROM fs WHERE id = ?', (file_id,))

            rows = c.fetchall()
            if len(rows) > 0:
                metadata = json.loads(rows[0][0])

            c.close()

        return metadata

    def getFileSize(self, file_id):
        if file_id:
            c = self.db.cursor()
            c.execute('SELECT size FROM fs WHERE id = ?', (file_id,))

            rows = c.fetchall()
            c.close()
            if len(rows) > 0:
                return rows[0][0]

        return 0

    def listFiles(self):
        c = self.db.cursor()
        c.execute('SELECT id, size, filename FROM fs')
        files = c.fetchall()
        c.close()
        return files


    #
    # Table (used for storing data time series)
    #

    def create_table(self, table_id):
        c = self.db.cursor()
        c.execute("CREATE TABLE '%s' (id char(7), data text)" % (table_id,))
        c.close()
        self.db.commit()

    def remove_table(self, table_id):
        c = self.db.cursor()
        c.execute("DROP TABLE '%s'" % (table_id,))
        self.db.commit()
        c.close()

    def get_table_rows(self, table_id, query = None, start=0, length=None, keys=None, sort=None):
        rows = []
        c = self.db.cursor()
        for row in c.execute("SELECT data FROM '%s'" % (table_id, )):
            rows.append(json.loads(row[0], cls=Decoder))
        c.close()

        if query:
            parser = TableQueryParser(compiler=attribute_compiler, tz=getattr(self, 'tz', None))
            filter_fn = parser.compile(query)
            rows = filter(filter_fn, rows)

        if sort:
            sort_attr = sort[0][0]
            asc = sort[0][1]
            rows = sorted(rows, key=lambda r: getattr(r, sort_attr, None), reverse=not asc)

            start = start or 0

        rows = rows[start:(length + start if length is not None else None)]
        
        if keys:
            rows = [filter_obj(row, keys) for row in rows]
        
        return rows

    def insert_table_row(self, table_id, row_data):
        c = self.db.cursor()
        c.execute("INSERT INTO '%s' (id, data) VALUES (?, ?)" % table_id, (row_data['id'], json.dumps(row_data, cls=Encoder)))
        row_data['id'] = c.lastrowid
        self.db.commit()
        c.close()

    def update_table_row(self, table_id, row_id, row_data):
        """return the old row"""
        c = self.db.cursor()

        c.execute("SELECT data FROM '%s' WHERE id = ?" % table_id, (row_id,))
        updated_row = c.fetchone()
        if updated_row:
            updated_row = json.loads(updated_row[0], cls=Decoder)

        c.execute(
            "UPDATE '%s' SET data = ? WHERE id = ?" % table_id,
            (json.dumps(row_data, cls=Encoder), row_id))

        self.db.commit()
        c.close()

        return updated_row

    def remove_table_row(self, table_id, row_id):
        """return the removed row"""
        c = self.db.cursor()

        c.execute("SELECT data FROM '%s' WHERE id = ?" % table_id, (row_id,))
        deleted_row = c.fetchone()
        if deleted_row:
            deleted_row = json.loads(deleted_row[0], cls=Decoder)

        c.execute("DELETE FROM '%s' WHERE id = ?" % table_id, (row_id,))

        self.db.commit()
        c.close()

        return deleted_row
