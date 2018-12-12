# coding: utf-8

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty
from collections import OrderedDict
import copy
from time import time
from ..ShortId import ShortId


class Driver_Base(object):

    def connect(self, cache):
        self.cache = cache

    def disconnect(self):
        pass

    def load_table_data(self, table_name):
        raise NotImplementedError()

    def list_tables(self):
        raise NotImplementedError()

    def get_file_content(self, file_id):
        raise NotImplementedError()

    def commit(self, commands):
        raise NotImplementedError()


class Dummy_Driver(Driver_Base):
    def load_table_data(self, table_name):
        return []

    def list_tables(self):
        return []

    def get_file_content(self, file_id):
        return b''

    def commit(self, commands):
        for cmd in commands:
            pass


class Db(object):
    def __init__(self, driver, auto_commit=False, cache_delay=3600, auto_connect=True):
        self._driver = driver
        self._auto_commit = auto_commit
        self._cache_delay = cache_delay
        self._fs = None
        self._connected = False

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

        self._driver.connect(self)

        for table_name in self._driver.list_tables():
            table = Table(self, table_name)
            self._tables.append(table)

        self._connected = True

    def disconnect(self):
        self._connected = False
        self.commit()
        self._driver.disconnect()

    @property
    def connected(self):
        return self._connected

    @property
    def fs(self):
        # lazy load
        if self._fs is None:
            self._fs = FS(self)
        return self._fs

    def get_table(self, table_name):
        for t in self._tables:
            if t.name == table_name:
                return t
        raise KeyError('the table %s does not exist' % table_name)

    def table_exists(self, table_name):
        for t in self._tables:
            if t.name == table_name:
                return True
        return False

    def list_tables(self):
        return [t.name for t in self._tables]

    def __getitem__(self, table_name):
        return self.get_table(table_name)

    def _add_cmd(self, cmd):
        self._journal.put(cmd)

    def create(self, table_name):

        if self.table_exists(table_name):
            raise Exception('create error: table "%s" already exists' % table_name)

        self._add_cmd(Create_Command(table_name))
        table = Table(self, table_name, True)
        self._tables.append(table)

        self._commit()

        return table

    def drop(self, table_name):
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
            raise Exception('drop error: table "%s" does not exist' % table_name)
        self._commit()

    def commit(self):
        cmds = []
        while True:
            try:
                cmds.append(self._journal.get(False))
            except Empty:
                break
        if cmds:
            self._driver.commit(cmds)

    def need_commit(self):
        return not self._journal.empty()

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
            self.drop(table_name)

    def _commit(self):
        if self._auto_commit:
            self.commit()


class Table(object):
    def __init__(self, db, name, empty=False):
        self._db = db
        self._driver = self._db._driver
        self._name = name
        self._data = OrderedDict() if empty else None
        self._auto_commit = self._db._auto_commit
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
            data = filter(filter_fn, self._data.values())
        else:
            data = self._data.values()

        if sort is not None:
            sort_attr = sort[0]
            asc = sort[1]
            data = sorted(data, key=lambda doc: doc.get(sort_attr, None), reverse=not asc)
        else:
            data = list(data)

        if start or length:
            data = data[start:(length + start if length is not None else None)]

        return [copy.deepcopy(doc) for doc in data]

    def insert(self, doc):
        self._lazy_load()

        doc = copy.deepcopy(doc)
        doc_id = doc['id']

        if doc_id in self._data:
            raise Exception('insert error: doc with id %s already exist' % doc_id)

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
            raise Exception('delete error: doc with id %s does not exist' % doc_id)

        self._db._add_cmd(Delete_Command(self.name, doc_id))
        del self._data[doc_id]
        self._commit()

    def clear(self):
        self._data = OrderedDict()
        self._db._add_cmd(Clear_Command(self.name))
        self._commit()

    def _commit(self):
        self._activity = time()
        if self._auto_commit:
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
                self._db.create('fs')
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

    def create(self, filename, **metadata):

        file_id = ShortId.generate()

        meta = {
            'id': file_id,
            'filename': filename,
            'size': 0
        }
        meta.update(metadata)
        self._meta.insert(meta)

        file = File(self, data=b'', meta=meta)
        self._files[file_id] = file
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
        if self._db._auto_commit:
            self._db.commit()


class File(object):
    def __init__(self, fs, data=None, meta=None):
        self._fs = fs
        self._db = fs._db
        self._driver = self._db._driver
        self._meta = meta or dict()
        self._meta.setdefault('size', 0)
        self._data = data
        self._auto_commit = self._db._auto_commit
        self._activity = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s id=%s filename=%s size=%d>' % (type(self).__name__, self.id, self._meta.get('filename'), self._meta.get('size', 0))

    @property
    def id(self):
        return self._meta['id']

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
        self['size'] = len(content)
        self._db._add_cmd(FS_Write_Command(self.id, content))
        self._commit()

    def clear(self):
        self.write(b'')

    def _commit(self):
        self._activity = time()
        if self._auto_commit:
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


if __name__ == '__main__':

    db = Db(Dummy_Driver(), auto_commit=True)

    table = db.create('toto')


    def init(t):
        for i in range(10):
            t.insert({
                'id': i
            })


    init(table)

    # db.commit()

    print(table.select(sort=('id', True), filter_fn=lambda r: r.get('id') < 10))

    file = db.fs.create('toto', version='1.0.0')

    print(file.id)
    assert file['size'] == 0
    assert file['version'] == '1.0.0'

    content = b'hello world'

    file.write(content)

    assert file['size'] == len(content)
    assert file.read() == content

    print(file.read())

    assert db.fs.get(file.id) is file

    #db.fs.remove(file)

    db.clear()

    db.fs.create('tata', version='1.0.0')






