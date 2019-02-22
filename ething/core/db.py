
# coding: utf-8
from future.utils import string_types
try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
from .reg import *
from .utils import object_sort, ShortId
from collections import OrderedDict, MutableMapping
import copy
from time import time
import inspect
import logging
import re


LOGGER = logging.getLogger('ething.db')


class Driver_Base(object):

    def connect(self):
        pass

    def disconnect(self):
        pass

    def load_table_data(self, table_name):
        raise NotImplementedError()

    def list_tables(self):
        raise NotImplementedError()

    def get_file_content(self, file_id):
        raise NotImplementedError()

    def process_command(self, command):
        raise NotImplementedError()
    
    def commit(self, commands):
      for cmd in commands:
          self.process_command(cmd)
    
    def get_usage(self):
      return 0


class Dummy_Driver(Driver_Base):
    def load_table_data(self, table_name):
        return []

    def list_tables(self):
        return []

    def get_file_content(self, file_id):
        return b''

    def process_command(self, command):
        pass


class Db(object):
    def __init__(self, driver, auto_commit=False, cache_delay=3600, auto_connect=True):
        self._driver = driver
        self._auto_commit = auto_commit
        self._cache_delay = cache_delay
        self._fs = FS(self)
        self._os = OS(self)
        self._store = Store(self)
        self._connected = False
        self._commiting = False

        if auto_connect:
            self.connect()

    @property
    def auto_commit(self):
        return self._auto_commit

    @property
    def cache_delay(self):
        return self._cache_delay

    def connect(self):
        self._journal = Queue()
        self._tables = []

        self._driver.connect()

        for table_name in self._driver.list_tables():
            table = Table(self, table_name)
            self._tables.append(table)

        self._connected = True

    def disconnect(self):
        if self._connected:
            self._connected = False
            self.commit()
            self._driver.disconnect()

    @property
    def connected(self):
        return self._connected

    @property
    def fs(self):
        return self._fs
    
    @property
    def os(self):
        return self._os

    @property
    def store(self):
        return self._store

    def get_usage(self):
        return self._driver.get_usage()

    # table
    def table_get(self, table_name, autocreate=True):
        for t in self._tables:
            if t.name == table_name:
                return t
        if autocreate:
          return self.table_create(table_name)
        else:
          raise KeyError('the table %s does not exist' % table_name)

    def table_exists(self, table_name):
        for t in self._tables:
            if t.name == table_name:
                return True
        return False

    def table_list(self):
        return [t.name for t in self._tables]

    def table_create(self, table_name):

        if self.table_exists(table_name):
            raise Exception('create error: table "%s" already exists' % table_name)

        self._add_cmd(Create_Command(table_name))
        table = Table(self, table_name, True)
        self._tables.append(table)

        self._commit()

        return table

    def table_drop(self, table_name, silent=False):
        if isinstance(table_name, Table):
            table_name = table_name.name
        for i in range(len(self._tables)):
            if self._tables[i].name == table_name:
                table = self._tables[i]
                self._add_cmd(Drop_Command(table_name))
                del self._tables[i]
                table._free()
                break
        else:
            if not silent:
                raise Exception('drop error: table "%s" does not exist' % table_name)
        self._commit()

    #
    def commit(self):
        if self._commiting: return

        self._commiting = True

        try:
            self.os.commit()

            cmds = []
            while True:
                try:
                    cmds.append(self._journal.get(False))
                except Empty:
                    break
            if cmds:
                self._driver.commit(cmds)
        finally:
            self._commiting = False

    def need_commit(self):
        return not self._journal.empty() or self.os.need_commit()

    def run_garbage_collector(self):
        now = time()
        for table in self._tables:
            if table.loaded:
                if now - table.activity > self._cache_delay:
                    table._free()

        if self._fs is not None:
            self._fs.run_garbage_collector()

    def clear(self):
        if self._fs is not None:
            self._fs.clear()

        for table_name in list(map(lambda t: t.name, self._tables)):
            self.table_drop(table_name)

    def _commit(self):
        if self._auto_commit:
            self.commit()
    
    def __getitem__(self, table_name):
        return self.table_get(table_name)

    def _add_cmd(self, cmd):
        self._journal.put(cmd)


class Table(MutableMapping):
    def __init__(self, db, name, empty=False):
        self._db = db
        self._driver = self._db._driver
        self._name = name
        self._data = OrderedDict() if empty else None
        self._activity = time() if empty else None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s name=%s>' % (type(self).__name__, self._name)

    @property
    def name(self):
        return self._name

    @property
    def activity(self):
        return self._activity

    @property
    def loaded(self):
        return self._data is not None

    @property
    def length(self):
        self._lazy_load()
        return len(self._data)

    def get_doc(self, doc_id):
        self._lazy_load()
        return copy.deepcopy(self._data[doc_id])

    def __getitem__(self, doc_id):
        return self.get_doc(doc_id)

    def __setitem__(self, doc_id, doc):
        if doc_id != doc['id']:
            raise KeyError()
        self.update(doc)

    def __delitem__(self, doc_id):
        self.delete(doc_id)

    def __len__(self):
        self._lazy_load()
        return len(self._data)

    def __iter__(self):
        self._lazy_load()
        return iter(self._data)

    def _load(self):
        table_data = self._driver.load_table_data(self.name)

        # Note : table_data must be ordered by inserting date !

        self._data = OrderedDict()

        for doc in table_data:
            doc_id = doc.get('id')
            self._data[doc_id] = doc

    def _lazy_load(self):
        self._activity = time()
        if self._data is None:
            self._load()

    def _free(self):
        self._data = None
        self._activity = None

    def select(self, sort=None, filter_fn=None, start=0, length=None):
        self._lazy_load()

        if filter_fn is not None:
            data = list(filter(filter_fn, self._data.values()))
        else:
            data = list(self._data.values())

        if sort is not None:
            sort_attr = sort[0]
            asc = sort[1]
            data = object_sort(data, key=lambda doc: doc.get(sort_attr, None), reverse=not asc)

        if start or length:
            data = data[start:(length + start if length is not None else None)]

        return [copy.deepcopy(doc) for doc in data]

    def insert(self, doc):
        self._lazy_load()

        doc = copy.deepcopy(doc)
        doc_id = doc['id']

        if doc_id in self._data:
            raise KeyError('insert error: doc with id %s already exist' % doc_id)

        self._db._add_cmd(Insert_Command(self.name, doc))
        self._data[doc_id] = doc
        self._commit()

        return doc

    def update(self, doc):
        self._lazy_load()

        doc_id = doc['id']

        if doc_id in self._data:
            # update
            self._db._add_cmd(Update_Command(self.name, doc))
            self._data[doc_id].update(doc)
            self._commit()
        else:
            # insert
            self.insert(doc)

    def delete(self, doc_id):
        self._lazy_load()

        if doc_id not in self._data:
            raise KeyError('delete error: doc with id %s does not exist' % doc_id)

        self._db._add_cmd(Delete_Command(self.name, doc_id))
        del self._data[doc_id]
        self._commit()

    def clear(self):
        self._data = OrderedDict()
        self._db._add_cmd(Clear_Command(self.name))
        self._commit()

    def _commit(self):
        self._activity = time()
        self._db.commit()


class FS(object):
    def __init__(self, db):
        self._db = db
        self._driver = self._db._driver

        self.__table = None
        self.__files = None

    @property
    def _meta(self):
        if self.__table is None:
            if not self._db.table_exists('fs'):
                self._db.table_create('fs')
            self.__table = self._db['fs']
        return self.__table

    @property
    def _files(self):
        if self.__files is None:
            self.__files = dict()
            for file_meta in self._meta.select():
                file = File(self, meta=file_meta)
                self.__files[file.id] = file
        return self.__files

    def list(self):
        return list(self._files.values())

    def exists(self, file_id):
        return file_id in self._files

    def create(self, filename, content=None, **metadata):

        file_id = ShortId.generate()

        metadata.update({
            'id': file_id,
            'filename': filename,
            'size': 0
        })

        self._meta.insert(metadata)

        file = File(self, data=b'', meta=metadata)
        self._files[file_id] = file

        if content is not None:
          file.write(content)
        
        return file

    def __getitem__(self, file_id):
        return self.get(file_id)

    def get(self, file_id):
        if isinstance(file_id, File):
            file_id = file_id.id
        #if file_id not in self._files:
        #    meta = self._meta[file_id]
        #    file = File(self, meta=meta)#
        #    self._files[file_id] = file
        if file_id not in self._files:
            raise Exception('fs error: file %s does not exist' % file_id)
        return self._files[file_id]

    def remove(self, file_id):
        if isinstance(file_id, File):
            file_id = file_id.id
        self._meta.delete(file_id)
        if file_id in self._files:
            file = self._files[file_id]
            del self._files[file_id]
            file._free()
        self._db._add_cmd(FS_Delete_Command(file_id))
        self._commit()

    def run_garbage_collector(self):
        if self.__files is None: return # nothing loaded from now
        now = time()
        for file_id in self._files:
            file = self._files[file_id]
            if file.loaded:
                if now - file.activity > self._db._cache_delay:
                    file._free()

    def clear(self):
        for file_id in map(lambda f: f.id, self.list()):
            self.remove(file_id)
        self.__table = None

    def _commit(self):
        self._db.commit()


class File(object):
    def __init__(self, fs, data=None, meta=None):
        self._fs = fs
        self._db = fs._db
        self._driver = self._db._driver
        self._meta = meta or dict()
        self._meta.setdefault('size', 0)
        self._data = data
        self._activity = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s id=%s filename=%s size=%d>' % (type(self).__name__, self.id, self.filename, self.size)

    @property
    def id(self):
        return self._meta.get('id')

    @property
    def filename(self):
        return self._meta.get('filename')

    @property
    def size(self):
        return self._meta.get('size', 0)

    @property
    def metadata(self):
        return copy.deepcopy(self._meta)

    @property
    def activity(self):
        return self._activity

    @property
    def loaded(self):
        return self._data is not None

    def __getitem__(self, key):
        return self._meta.get(key)

    def __setitem__(self, key, value):
        self._meta[key] = value
        self._fs._meta.update(self._meta)

    def _lazy_load(self):
        self._activity = time()
        if self._data is None:
            self._data = self._driver.get_file_content(self.id)

    def _free(self):
        self._data = None
        self._activity = None

    def read(self):
        self._lazy_load()
        return self._data

    def write(self, content):
        self._data = content
        self._meta['size'] = len(content)
        self._db._add_cmd(FS_Write_Command(self.id, content))
        self._commit()

    def clear(self):
        self.write(b'')

    def _commit(self):
        self._activity = time()
        self._db.commit()



class Command_Base(object):
    def __init__(self, name=None):
        self.name = name or type(self).__name__

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s>' % (self.name,)


class Table_Command_Base(Command_Base):
    def __init__(self, table_name, name=None):
        super(Table_Command_Base, self).__init__(name)
        self.table_name = table_name

    def __str__(self):
        return '<%s table=%s>' % (self.name, self.table_name)


class Doc_Command_Base(Table_Command_Base):
    def __init__(self, table_name, doc_id, name=None):
        super(Doc_Command_Base, self).__init__(table_name, name)
        self.doc_id = doc_id

    def __str__(self):
        return '<%s table=%s doc_id=%s>' % (self.name, self.table_name, self.doc_id)


class Update_Command(Doc_Command_Base):
    def __init__(self, table_name, doc):
        super(Update_Command, self).__init__(table_name, doc.get('id'), name='update')
        self.doc = doc


class Insert_Command(Doc_Command_Base):
    def __init__(self, table_name, doc):
        super(Insert_Command, self).__init__(table_name, doc.get('id'), name='insert')
        self.doc = doc


class Delete_Command(Doc_Command_Base):
    def __init__(self, table_name, doc_id):
        super(Delete_Command, self).__init__(table_name, doc_id, name='delete')


class Create_Command(Table_Command_Base):
    def __init__(self, table_name):
        super(Create_Command, self).__init__(table_name, name='create')


class Drop_Command(Table_Command_Base):
    def __init__(self, table_name):
        super(Drop_Command, self).__init__(table_name, name='drop')


class Clear_Command(Table_Command_Base):
    def __init__(self, table_name):
        super(Clear_Command, self).__init__(table_name, name='clear')


class File_Command_Base(Command_Base):
    def __init__(self, file_id, name=None):
        super(File_Command_Base, self).__init__(name)
        self.file_id = file_id

    def __str__(self):
        return '<%s file_id=%s>' % (self.name, self.file_id)


class FS_Delete_Command(File_Command_Base):
    def __init__(self, file_id):
        super(FS_Delete_Command, self).__init__(file_id, name='fs.delete')


class FS_Write_Command(File_Command_Base):
    def __init__(self, file_id, content):
        super(FS_Write_Command, self).__init__(file_id, name='fs.write')
        self.content = content

    def __str__(self):
        return '<%s file_id=%s len=%d>' % (self.name, self.file_id, len(self.content))


class OS(object):

  def __init__(self, db):
    self._db = db
    self._dirty = False
    self.__items = dict()
    self._context = {
      '__db': self._db
    }

  @property
  def context(self):
    return self._context
    
  def _get_os(self, cls):
    if not inspect.isclass(cls):
      cls = type(cls)
    
    table_name = get_meta(cls, 'table', cls.__name__)

    if table_name not in self.__items:
      self.__items[table_name] = OS_item(cls, self)
    
    return self.__items[table_name]

  def __getitem__(self, cls):
    return self._get_os(cls)

  def update_context(self, cls, context):
    return self._get_os(cls).update_context(context)
  
  def find(self, cls, *args, **kwargs):
    return self._get_os(cls).find(*args, **kwargs)
  
  def get(self, cls, id):
    return self._get_os(cls).get(id)
  
  def save(self, obj):
    return self._get_os(obj).save(obj)
  
  def remove(self, obj):
    return self._get_os(obj).remove(obj)
  
  def create(self, cls, data=None):
    return self._get_os(cls).create(data)
  
  def commit(self):
    self._dirty = False
    for table_name in self.__items:
      os_item = self.__items[table_name]
      os_item.commit()

  def need_commit(self):
      return self._dirty


class OS_item(object):

  def __init__(self, cls, os):
    self._os = os
    self._db = os._db
    self._cls = cls
    self._auto_commit = self._db._auto_commit
    self._ref = dict()
    self._dirty_obj = set() # only if auto_commit is False
    self._loaded = False
    self._saving = set()
    self._table_name = get_meta(cls, 'table', cls.__name__)
    self._id_key = get_meta(cls, 'id_key', 'id')
    if not has_registered_attr(cls, self._id_key):
      raise Exception('%s class has no attribute "%s"' % (cls.__name__, self._id_key))
    self._table = self._db[self._table_name]
    self._context = dict()

  @property
  def context(self):
      c = self._os.context.copy()
      c.update(self._context)
      return c

  def update_context(self, c):
      self._context.update(c)

  def create(self, data=None):
    obj = create(self._cls, data, self.context)
    self.save(obj)
    return obj
  
  def load(self):
    if self._loaded:
      return

    self._loaded = True

    context = self.context
    rows = self._table.select()
    for doc in rows:
      try:
          obj = unserialize(self._cls, doc, context)
          id = getattr(obj, self._id_key)
          if id not in self._ref: # do not erase previous reference
            self._ref[id] = obj
      except:
          LOGGER.exception('unable to unserialize a %s' % self._cls.__name__)

    LOGGER.debug('[%s] %d items loaded' % (self._cls.__name__, len(self._ref)))

  def find(self, query=None, sort=None, skip=None, limit=None):
    self.load()

    objs = list(self._ref.values())

    if query:
        objs = [r for r in objs if query(r)]

    if isinstance(sort, string_types):
        m = re.search('^([+-]?)(.+)$', sort)
        if m is not None:
            asc = m.group(1) != '-'
            sort_attr = m.group(2)

            objs = object_sort(objs, key=lambda r: getattr(r, sort_attr, None), reverse = not asc)

    offset = skip or 0

    return objs[offset:(limit + offset if limit is not None else None)]
  
  def get(self, id):
    self.load()
    return self._ref[id]
  
  def save(self, obj, force=False, _create=False):

    id = getattr(obj, self._id_key)

    if id in self._saving:
        return

    reg = install(obj)
    if '__db' not in reg.context:
        # no database attached to this instance
        reg.context['__db'] = self._db

    _create = id not in self._ref

    if not _create and not force and not is_dirty(obj):
      return # nothing to save

    if hasattr(obj, '__db_save__'):
        # be careful here, because save() may be called again
        self._saving.add(id)
        try:
            obj.__db_save__(_create)
        finally:
            self._saving.discard(id)

    LOGGER.debug('[%s] saving %s' % (self._cls.__name__, obj))

    # save the ref
    self._ref[id] = obj

    if self._auto_commit:
      self._table.update(serialize(obj))
    else:
      self.mark_dirty(id)
    
    clean(obj)
  
  def remove(self, obj):
    id = getattr(obj, self._id_key)
    self._dirty_obj.discard(id)
    if id in self._ref:
        if hasattr(obj, '__db_remove__'):
            obj.__db_remove__()
        del self._ref[id]
    else:
      if self._loaded:
        raise Exception('unable to remove object class=%s id=%s : not exist' % (self._cls.__name__, id))
    try:
      self._table.delete(id)
    except:
      pass # silent
  
  def mark_dirty(self, id):
      self._dirty_obj.add(id)
      self._os._dirty = True

  def commit(self):
    for id in self._dirty_obj:
      self._table.update(serialize(self._ref[id]))
    self._dirty_obj.clear()
  
  
def db(table=None, id_key=None, database=None):
  def d(cls):
    if table is not None: set_meta(cls, 'table', table)
    if id_key is not None: set_meta(cls, 'id_key', id_key)
    if database is not None: set_meta(cls, 'database', database)

    original_watch = getattr(cls, '__watch__', None)

    def __watch__(self, attribute, val, old_val):
      if original_watch is not None:
        original_watch(self, attribute, val, old_val)
      
      t = self.__reg__.context.get('__transaction', 0)
      if t == 0:
        save(self)
    
    setattr(cls, '__watch__', __watch__)

    return cls
  return d


class transaction(object):

  def __init__(self, obj):
    self._obj = obj
    self._reg = install(obj)
  
  def __enter__(self):
    t = self._reg.context.get('__transaction', 0)
    self._reg.context['__transaction'] = t+1
    return self._obj
  
  def __exit__(self, type, value, traceback):
    t = self._reg.context['__transaction']
    t = t - 1
    try:
      if t==0: save(self._obj)
    finally:
      self._reg.context['__transaction'] = t


def _get_db(obj):
    # retrieve the database from the context
    _db = get_context(obj).get('__db')
    if _db is None:
        # retrieve from the metadata
        _db = get_meta(obj, 'database')
        if _db is None:
            raise Exception('no database set for %s' % obj)

    return _db


def save(obj):
    return _get_db(obj).os.save(obj)


def remove(obj):
    return _get_db(obj).os.remove(obj)


def db_create(cls, data=None):
    return get_meta(cls, 'database').os.create(cls, data)


def db_get(cls, id):
  return get_meta(cls, 'database').os.get(cls, id)


def db_find(cls, *args, **kwargs):
  return get_meta(cls, 'database').os.find(cls, *args, **kwargs)


def db_id(obj):
    key = get_meta(obj, 'id_key', 'id')
    return getattr(obj, key)


# key-value store

class Store(MutableMapping):

    def __init__(self, db):
        self._db = db
        self._id = 1
        self._store = {
            'id': self._id
        }
        self._loaded = False
        self.__table = None

    @property
    def _table(self):
        if self.__table is None:
            self.__table = self._db['store']
        return self.__table

    def _load(self):
        if not self._loaded:
            self._loaded = True
            try:
                store = self._table[self._id]
            except KeyError:
                pass
            else:
                store.update(self._store)
                self._store = store

    def _commit(self):
        self._table[self._id] = self._store

    def __getitem__(self, key):
        if key == 'id':
            raise KeyError('invalid key')
        self._load()
        return self._store[key]

    def __setitem__(self, key, value):
        if key == 'id':
            raise KeyError('invalid key')
        self._store[key] = value
        self._commit()

    def __delitem__(self, key):
        if key == 'id':
            raise KeyError('invalid key')
        self._load()
        if key in self._store:
            del self._store[key]
            self._commit()

    def __len__(self):
        self._load()
        return len(self._store) - 1

    def __iter__(self):
        self._load()
        return iter([k for k in self._store if k != 'id'])


class DBLink(String):

    def __init__(self, cls, **attributes):
        super(DBLink, self).__init__(allow_empty=False, **attributes)
        if isinstance(cls, string_types):
            self._clsname = cls
            self._cls = None
        else:
            self._cls = cls

    @property
    def cls(self):
        if self._cls is None:
            self._cls = get_registered_class(self._clsname)
        return self._cls

    def _db_get(self, id, context=None):
        # throw KeyError if the id does not exist
        try:
            if context is not None and '__db' in context:
                return context['__db'].os.get(self.cls, id)
            return db_get(self.cls, id)
        except KeyError:
            raise ValueError('the %s object with id=%s does not exist' % (self.cls.__name__, id))

    def check(self, obj):
        pass

    def get(self, value, context=None):
        return self._db_get(value, context)

    def set(self, value, context=None):
        if isinstance(value, string_types):
            value = super(DBLink, self).set(value, context)
            # check the id exist !
            obj = self._db_get(value, context)
            self.check(obj)
        else:
            self.check(value)
            value = db_id(value)
        return value

    def fromJson(self, value, context=None):
        value = super(DBLink, self).fromJson(value, context)
        # check the id exist !
        obj = self._db_get(value, context)
        self.check(obj)
        return value
