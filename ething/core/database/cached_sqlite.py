# coding: utf-8

from .base import LOGGER
from .cache import Driver_Base
from .cachedb import CacheDB
from .sqlite import Decoder, Encoder, to_timestamp, py3, Connection, sqlite3, USER_DIR
from ..utils.lock import SecureLock
import os
import json
import pytz


class SQLiteDriver(Driver_Base):

    def __init__(self, database):
        super(SQLiteDriver, self).__init__()
        if database == ':memory:':
            self.file = None
        else:
            self.file = os.path.join(USER_DIR, '%s.cache.db' % database)
        self._lock = SecureLock(name='sqlite')

    def connect(self, cache):
        super(SQLiteDriver, self).connect(cache)

        with self._lock:
            self.db = sqlite3.connect(self.file or ':memory:', check_same_thread=False, factory=Connection)

            if self.db is None:
                raise Exception('unable to connect to the database')

            LOGGER.info('connected to database: %s' % (self.file or 'memory'))

            c = self.db.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS __fs_data (id char(7), content blob)')
            self.db.commit()
            c.close()

    def disconnect(self):
        if hasattr(self, 'db'):
            with self._lock:
                self.db.commit()
                self.db.close()

    def load_table_data(self, table_name):
        with self._lock:
            c = self.db.cursor()
            c.execute("SELECT data FROM '%s'" % (table_name,))
            _rows = c.fetchall()
            c.close()

        return [json.loads(row[0], cls=Decoder) for row in _rows]

    def list_tables(self):
        with self._lock:
            c = self.db.cursor()
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = c.fetchall()
            c.close()
        return [t[0] for t in tables if not t[0].startswith('__')]

    def get_file_content(self, file_id):
        content = None
        with self._lock:
            c = self.db.cursor()
            c.execute('SELECT content FROM __fs_data WHERE id = ? LIMIT 1', (file_id,))

            file = c.fetchone()
            if file:
                content = file[0]
                if not py3 and isinstance(content, buffer):
                    content = str(content)  # convert buffer to string

            c.close()
        return content

    def _process_command(self, c, cmd):

        if cmd.name == 'update':
            c.execute(
                "UPDATE '%s' SET data = ?, date = ? WHERE id = ?" % cmd.table_name,
                (json.dumps(cmd.doc, cls=Encoder), to_timestamp(cmd.doc.get('date')), cmd.doc_id))

        elif cmd.name == 'insert':
            c.execute("INSERT INTO '%s' (id, date, data) VALUES (?, ?, ?)" % cmd.table_name,
                      (cmd.doc_id, to_timestamp(cmd.doc.get('date')), json.dumps(cmd.doc, cls=Encoder)))

        elif cmd.name == 'delete':
            c.execute("DELETE FROM '%s' WHERE id = ?" % cmd.table_name, (cmd.doc_id,))

        elif cmd.name == 'create':
            c.execute("CREATE TABLE '%s' (id char(7), date integer, data json)" % (cmd.table_name,))

        elif cmd.name == 'drop':
            c.execute("DROP TABLE '%s'" % (cmd.table_name,))

        elif cmd.name == 'clear':
            c.execute("DELETE FROM '%s'" % cmd.table_name)

        elif cmd.name == 'fs.write':
            c.execute("INSERT INTO __fs_data (id, content) VALUES (?, ?)",
                        (cmd.file_id, sqlite3.Binary(cmd.content)))

        elif cmd.name == 'fs.delete':
            c.execute("DELETE FROM __fs_data WHERE id = ?", (cmd.file_id,))

        else:
            LOGGER.error('unknown command %s' % cmd)

    def commit(self, commands):
        with self._lock:
            c = self.db.cursor()
            for cmd in commands:
                self._process_command(c, cmd)
            c.close()
            self.db.commit()


class CachedSQLite(CacheDB):

    def __init__(self, core, **config):
        super(CachedSQLite, self).__init__(core, SQLiteDriver(config.get('database')), **config)

    def get_usage(self):
        try:
            db_file = self._cachedb._driver.file
            return os.path.getsize(db_file) if db_file else 0
        except:
            return 0

    def clear(self):
        self.disconnect()
        db_file = self._cachedb._driver.file
        if db_file:
            os.remove(db_file)
        self.connect()
