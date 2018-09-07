# coding: utf-8

from __future__ import unicode_literals
from future.utils import string_types, integer_types, iteritems
import os
import logging
import json
import re
import copy
from hashlib import md5
from pytz import common_timezones
from collections import OrderedDict
import threading


CONF_VERSION = 1


class Config(object):

    # default configuration
    DEFAULT = {

        # mongoDB server
        'db': {
            'type': 'sqlite', # sqlite or mongodb
            # 'host': 'localhost',
            # 'port': 27017,
            # 'user': None,
            # 'password': None,
            'database': "ething"
        },

        # (set to false to disable this feature)
        'notification': {
            'emails': [],

            # 'smtp' :
            #    'host': 'smtp.gmail.com',
            #    'port' : 587,
            #    'user' : '<username>@gmail.com',
            #    'password' : '<password>'

            'smtp': None
        },

        # debug information is given in the error messages send through HTTP requests
        'debug': False,

        # logging. Set to false to disable logging.
        'log': {
            'level': 'INFO'
        },

        # "mqtt" : {
        #    "host" : "localhost", # disabled by default
        #    "port" : 1883,
        #    "clientId" : "ething",
        #    "rootTopic" : "ething/"
        # },

        'script': {
            'timeout': 300000  # in millisecondes
        },

        'nodejs': {
            'executable': 'node'
        },

        'node-red': {
            'port': 1880,
            'target': ''  # http://localhost:1880
        },

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
                "properties": OrderedDict([
                    ("level", {
                        "type": "string",
                        "enum": ['DEBUG', 'INFO', 'WARNING', 'ERROR']
                    })
                ])
            }),
            ("script", {
                "type": "object",
                "properties": OrderedDict([
                    ("timeout", {
                        "description": "Expressed in milliseconds. 0 means unlimited.",
                        "type": "integer",
                        "minimum": 0
                    })
                ])
            }),
            ("notification", {
                "type": "object",
                "properties": OrderedDict([
                    ("smtp", {
                        "anyOf": [{
                            "type": "object",
                            "required": ['host', 'port', 'user', 'password'],
                            "properties": OrderedDict([
                                ("host", {
                                    "type": "string",
                                    "minLength": 1,
                                    "default": 'smtp.gmail.com'
                                }),
                                ("port", {
                                    "type": "integer",
                                    "title": "The Port Schema ",
                                    'type': 'integer',
                                    'minimum': 1,
                                    'maximum': 65535,
                                    "default": 587
                                }),
                                ("user", {
                                    "type": "string",
                                    "minLength": 1
                                }),
                                ("password", {
                                    "type": "string",
                                    "minLength": 1
                                })
                            ])
                        }, {
                            "type": "null"
                        }]
                    }),
                    ("emails", {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "minLength": 1
                        }
                    })
                ])
            })
        ])
    }

    def __init__(self, core, config=None):

        self.core = core

        self._lock = threading.Lock()

        self._d = copy.deepcopy(Config.DEFAULT)

        if isinstance(config, string_types):
            config = self.load(config)

        if isinstance(config, dict):
            self._d = Config.__merge(self._d, config)

    @staticmethod
    def load(filename):
        config = None

        if os.path.isfile(filename):
            # try to read it !
            config = json.load(open(filename))

        return config

    @staticmethod
    def __merge(dct, merge_dct):
        for k, v in iteritems(merge_dct):
            if k in dct and isinstance(dct[k], dict):
                Config.__merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]
        return dct

    def save(self, filename):
        with open(filename, 'w') as outfile:
            json.dump(self.get(), outfile, indent=1)

    # get/set attribute

    def get(self, name=None, default=None):
        with self._lock:
            if name is None:
                return self._d
            else:
                parts = name.split('.')
                p = self._d
                for part in parts:
                    if isinstance(p, dict) and (part in p):
                        p = p[part]
                    else:
                        return default
                return p

    def _set(self, name, value=None):

        changes = []

        if isinstance(name, dict):
            for key in name:
                changes += self._set(key, name[key])

        else:

            if value is not None and isinstance(value, dict):
                for key in value:
                    changes += self._set("%s.%s" % (name, key), value[key])

            else:

                if name == 'notification.emails':
                    ok = False
                    if isinstance(value, list):
                        ok = True
                        for email in value:
                            if not (isinstance(email, string_types) and re.match("[^@]+@[^@]+\.[^@]+", email)):
                                ok = False
                                break
                    if not ok:
                        raise Exception('emails must be an array of email')
                elif name == 'debug' or name == 'auth.localonly':
                    if not isinstance(value, bool):
                        raise Exception(name+" must be a boolean")
                elif name == 'auth.password':
                    if not(isinstance(value, string_types) and re.match("^.{4,}$", value)):
                        raise Exception(
                            name+' must be a string (min. length = 4 cahracters)')
                    value = md5(value).hexdigest()
                elif name == 'script.timeout':
                    if not(isinstance(value, integer_types) and value >= 0):
                        raise Exception(name+' must be an integer >= 0')
                elif name == 'notification' or name == 'notification.smtp' or name == 'log' or name == 'mqtt':
                    if value is not None:
                        raise Exception(name+" is invalid")
                elif (name == 'db.user' or name == 'db.password' or name == 'notification.smtp.user' or name == 'notification.smtp.password'
                      or name == 'mqtt.user' or name == 'mqtt.password'):
                    if (not isinstance(value, string_types) or not value) and value is not None:
                        raise Exception(name+" must be a non empty string")
                elif (name == 'db.host' or name == 'db.database'
                      or name == 'notification.smtp.host'
                      or name == 'mqtt.host' or name == 'mqtt.clientId'):
                    if not isinstance(value, string_types) or not value:
                        raise Exception(name+" must be a non empty string")
                elif name == 'mqtt.rootTopic' or name == 'node-red.target':
                    if not isinstance(value, string_types):
                        raise Exception(name+" must be a string")
                elif name == 'db.port' or name == 'webserver.port' or name == 'notification.smtp.port' or name == 'mqtt.port' or name == 'node-red.port':
                    if not(isinstance(value, integer_types) and value >= 0 and value <= 65535):
                        raise Exception(name+" must be a valid port number")
                elif name == 'log.level':
                    if not isinstance(value, string_types):
                        raise Exception(
                            name+" must be a valid log level string")
                    value = value.upper()
                    try:
                        getattr(logging, value)
                    except AttributeError:
                        raise Exception(
                            name+" must be a valid log level string")

                parts = name.split('.')
                last = parts.pop()
                p = self._d
                for part in parts:
                    if (not part in p) or not isinstance(p[part], dict):
                        p[part] = {}
                    p = p[part]

                old_value = p.get(last)
                if old_value != value:
                    changes.append((name, value, old_value))

                p[last] = value

        return changes

    def set(self, name, value=None):
        with self._lock:
            changes = self._set(name, value)
            self.core.dispatchSignal('ConfigUpdated', changes)

    def __call__(self, *args):
        args = list(args)

        if len(args) == 0:
            return self.get()
        if len(args) == 1 and isinstance(args[0], dict):
            return self.set(args[0])
        if len(args) == 1 and isinstance(args[0], string_types):
            return self.get(args[0])
        if len(args) == 2 and isinstance(args[0], string_types):
            return self.set(args[0], args[1])

        raise ValueError('invalid arguments')

    def __getitem__(self, name):
        return self.get(name)

    def toJson(self):
        with self._lock:
            return self._d
