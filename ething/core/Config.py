# coding: utf-8

from __future__ import unicode_literals
from collections import Mapping, OrderedDict, MutableMapping
from future.utils import iteritems, string_types
from jsonschema import validate
import copy
import threading
from pytz import common_timezones


def merge(dct, merge_dct):
    for k, v in iteritems(merge_dct):
        if k in dct and isinstance(dct[k], Mapping):
            merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]
    return dct


def set_defaults(dct, defaults):
  for k, v in iteritems(defaults):

    if k in dct:
      if isinstance(dct[k], Mapping) and isinstance(defaults[k], Mapping):
        set_defaults(dct[k], defaults[k])
    else:
      dct[k] = defaults[k]


def get_from_path(data, path):
  parts = path.split('.')
  p = data
  for part in parts:
      if isinstance(p, Mapping) and (part in p):
          p = p[part]
      else:
          raise KeyError('invalid key %s' % path)
  return p


def set_from_path(data, path, value, dict_cls = dict):

  parts = path.split('.')
  last = parts.pop()
  p = data
  for part in parts:
      if (not part in p):
          p[part] = dict_cls()
      elif not isinstance(p[part], MutableMapping):
          raise KeyError('invalid key')
      p = p[part]

  p[last] = value


def update(d, u):
    for k in u:
        v = u[k]
        if isinstance(v, Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class ConfigBase(Mapping):
    def __init__(self, value=None, schema=None):
        self._store = value if value is not None else dict()
        self._schema = schema
        self._lock = threading.RLock()
        if self._schema:
            validate(self._store, self._schema)

    @property
    def schema(self):
        return self._schema

    def update(self, data):
        with self._lock:
            if self._schema:
                dcopy = copy.deepcopy(self._store)
                update(dcopy, data)
                # raise an exception if the validation fail
                validate(dcopy, self._schema)

            # list the keys that has been updated
            updated_keys = []
            for k in data:
                if k not in self._store or self._store[k] != data[k]:
                    updated_keys.append(k)
            update(self._store, data)
            if updated_keys:
                self.on_change(updated_keys)

    def set(self, key, value):
        with self._lock:
            if key not in self._store or self._store[key] != value:
                if self._schema:
                    dcopy = copy.deepcopy(self._store)
                    set_from_path(dcopy, key, value)
                    # raise an exception if the validation fail
                    validate(dcopy, self._schema)

                set_from_path(self._store, key, value)
                self.on_change([key])

    def __getitem__(self, key):
        return get_from_path(self._store, key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def on_change(self, updated_keys):
        pass

    def toJson(self):
        with self._lock:
            return self._store

    def __call__(self, *args):
        args = list(args)

        if len(args) == 1 and isinstance(args[0], dict):
            return self.update(args[0])
        if len(args) == 1 and isinstance(args[0], string_types):
            return self.get(args[0])
        if len(args) == 2 and isinstance(args[0], string_types):
            return self.set(args[0], args[1])

        raise ValueError('invalid arguments')

    def export(self):
        return copy.deepcopy(self._store)


class Config(ConfigBase):
    def _notify_change(self, child):
        self.on_change([child.key])


class ConfigItem(ConfigBase):
    def __init__(self, parent, key, schema=None, defaults = None):
        if schema is None:
            # inherit from the parent
            if parent.schema:
                schema = parent.schema.get('properties', {}).get(key)

        if key not in parent:
            parent._store[key] = dict()

        if defaults:
            set_defaults(parent._store[key], defaults)

        super(ConfigItem, self).__init__(parent[key], schema)

        self._parent = parent
        self._key = key

    @property
    def key(self):
        return self._key

    @property
    def parent(self):
        return self._parent

    def on_change(self, updated_keys):
        self._parent._notify_change(self)


class CoreConfig(Config):
    # default configuration
    DEFAULT = {

        # mongoDB server
        'db': {
            'type': 'sqlite',  # sqlite or mongodb or unqlite
            # 'host': 'localhost',
            # 'port': 27017,
            # 'user': None,
            # 'password': None,
            'database': "ething"
        },

        # debug information is given in the error messages send through HTTP requests
        'debug': False,

        # logging. Set to false to disable logging.
        'log': {
            'level': 'INFO'
        }

    }

    SCHEMA = {
        "type": "object",
        "properties": OrderedDict([

            ("debug", {
                "type": "boolean",
                "description": "Set the aplication in debug mode.",
            }),
            ("timezone", {
                "enum": common_timezones,
                "description": "Set the application timezone.",
            }),

            ("log", {
                "type": "object",
                "additionalProperties": False,
                "properties": OrderedDict([
                    ("level", {
                        "type": "string",
                        "enum": ['DEBUG', 'INFO', 'WARNING', 'ERROR']
                    })
                ])
            })
        ])
    }

    def __init__(self, core, value=None):
        v = copy.deepcopy(self.DEFAULT)

        if value:
            merge(v, value)

        super(CoreConfig, self).__init__(v, self.SCHEMA)
        self.core = core

    def on_change(self, updated_keys):
        self.core.log.info('config updated: %s' % updated_keys)
        self.core.dispatchSignal('ConfigUpdated', updated_keys, self.toJson())

