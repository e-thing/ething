# coding: utf-8

from ..db import Driver_Base, LOGGER
from ..env import USER_DIR
import threading
from ..green import make_it_green
import os
import json
import pickle
import datetime
import pytz
import time
import sys
import sqlite3
from dateutil import parser


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


class SQLiteDriver(Driver_Base):

    def __init__(self, database):
        super(SQLiteDriver, self).__init__()
        if database == ':memory:':
            self.file = None
        else:
            self.file = os.path.join(USER_DIR, '%s.db' % database)
        self._lock = threading.Lock() # SecureLock(name='sqlite')

    def connect(self):
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
                delattr(self, 'db')

    def load_table_data(self, table_name):
        if not hasattr(self, 'db'):
            return []

        with self._lock:
            c = self.db.cursor()
            c.execute("SELECT data FROM '%s'" % (table_name,))
            _rows = c.fetchall()
            c.close()

        return [pickle.loads(row[0]) for row in _rows]

    def get_table_length(self, table_name):
        with self._lock:
            c = self.db.cursor()
            c.execute("SELECT COUNT(1) FROM '%s'" % (table_name,))
            data = c.fetchone()
            l = data[0]
            c.close()
        return l

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
                (pickle.dumps(cmd.doc), to_timestamp(cmd.doc.get('date')), cmd.doc_id))

        elif cmd.name == 'insert':
            c.execute("INSERT INTO '%s' (id, date, data) VALUES (?, ?, ?)" % cmd.table_name,
                      (cmd.doc_id, to_timestamp(cmd.doc.get('date')), pickle.dumps(cmd.doc)))

        elif cmd.name == 'delete':
            c.execute("DELETE FROM '%s' WHERE id = ?" % cmd.table_name, (cmd.doc_id,))

        elif cmd.name == 'create':
            c.execute("CREATE TABLE '%s' (id char(7), date integer, data text)" % (cmd.table_name,))

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

    def clear(self):
        connected = hasattr(self, 'db')
        if connected:
          self.disconnect()
        db_file = self.file
        try:
          if db_file:
              os.remove(db_file)
        finally:
          if connected:
            self.connect()
    
    def get_usage(self):
        try:
            db_file = self.file
            return os.path.getsize(db_file) if db_file else 0
        except:
            return 0

