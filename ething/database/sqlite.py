# coding: utf-8
from abc import ABC

from ..db import DriverBase, LOGGER
from ..env import USER_DIR
import os
import json
import pickle
import datetime
import pytz
import time
import aiosqlite
import aiofiles.os
from dateutil import parser


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.isoformat()
            }
        if isinstance(obj, bytes):
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
                d = parser.parse(obj['value'])
                # be sure to make it offset-aware (UTC)
                if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
                    d = d.replace(tzinfo=pytz.utc)
                return d
            if type == 'bytes':
                return obj['value'].encode('utf8')
        return obj


def to_timestamp(d):
    if d is not None:
        return time.mktime(d.timetuple())


class SQLiteDriver(DriverBase):

    def __init__(self, database):
        super(SQLiteDriver, self).__init__()
        if database == ':memory:':
            self.file = None
        else:
            self.file = os.path.join(USER_DIR, '%s.db' % database)

        self.db = None

    async def connect(self):
        if self.db is not None:
            # already connected
            return

        self.db = await aiosqlite.connect(self.file or ':memory:')

        if self.db is None:
            raise Exception('unable to connect to the database')

        LOGGER.info('connected to database: %s' % (self.file or 'memory'))

        cursor = await self.db.execute('CREATE TABLE IF NOT EXISTS __fs_data (id char(7), content blob)')
        await self.db.commit()
        await cursor.close()

    async def disconnect(self):
        if self.db is not None:
            await self.db.commit()
            await self.db.close()
            self.db = None

    async def load_table_data(self, table_name):
        if self.db is None:
            return []

        cursor = await self.db.execute("SELECT data FROM '%s'" % (table_name,))
        _rows = await cursor.fetchall()
        await cursor.close()

        return [pickle.loads(row[0]) for row in _rows]

    async def get_table_length(self, table_name):
        if self.db is None:
            return 0

        cursor = await self.db.execute("SELECT COUNT(1) FROM '%s'" % (table_name,))
        data = await cursor.fetchone()
        table_len = data[0]
        await cursor.close()

        return table_len

    async def list_tables(self):
        if self.db is None:
            return []

        cursor = await self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = await cursor.fetchall()
        await cursor.close()

        return [t[0] for t in tables if not t[0].startswith('__')]

    async def get_file_content(self, file_id):
        content = None
        if self.db is not None:
            cursor = await self.db.execute('SELECT content FROM __fs_data WHERE id = ? LIMIT 1', (file_id,))

            file = await cursor.fetchone()
            if file:
                content = file[0]

            await cursor.close()
        return content

    async def _process_command(self, c, cmd):

        if cmd.name == 'update':
            await c.execute(
                "UPDATE '%s' SET data = ?, date = ? WHERE id = ?" % cmd.table_name,
                (pickle.dumps(cmd.doc), to_timestamp(cmd.doc.get('date')), cmd.doc_id))

        elif cmd.name == 'insert':
            await c.execute("INSERT INTO '%s' (id, date, data) VALUES (?, ?, ?)" % cmd.table_name,
                            (cmd.doc_id, to_timestamp(cmd.doc.get('date')), pickle.dumps(cmd.doc)))

        elif cmd.name == 'delete':
            await c.execute("DELETE FROM '%s' WHERE id = ?" % cmd.table_name, (cmd.doc_id,))

        elif cmd.name == 'create':
            await c.execute("CREATE TABLE '%s' (id char(7), date integer, data text)" % (cmd.table_name,))

        elif cmd.name == 'drop':
            await c.execute("DROP TABLE '%s'" % (cmd.table_name,))

        elif cmd.name == 'clear':
            await c.execute("DELETE FROM '%s'" % cmd.table_name)

        elif cmd.name == 'fs.write':
            await c.execute("INSERT INTO __fs_data (id, content) VALUES (?, ?)",
                            (cmd.file_id, memoryview(cmd.content)))

        elif cmd.name == 'fs.delete':
            await c.execute("DELETE FROM __fs_data WHERE id = ?", (cmd.file_id,))

        else:
            LOGGER.error('unknown command %s' % cmd)

    async def commit(self, commands):
        if self.db is not None:
            c = await self.db.cursor()
            # note: use asyncio.gather ? not sure because the commands needs to be executed one after another
            for cmd in commands:
                await self._process_command(c, cmd)
            await c.close()
            await self.db.commit()

    async def clear(self):
        connected = self.db is not None
        if connected:
            await self.disconnect()
        db_file = self.file
        try:
            if db_file:
                # os.remove(db_file)
                await aiofiles.os.remove(db_file)
        finally:
            if connected:
                await self.connect()

    async def get_usage(self):
        try:
            db_file = self.file
            return aiofiles.os.path.getsize(db_file) if db_file else 0
        except:
            return 0
