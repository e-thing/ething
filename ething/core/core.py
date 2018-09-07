# coding: utf-8

from future.utils import string_types

from .reg import get_registered_class
from .database.mongodb import MongoDB
from .database.sql import SQL
from .ResourceQueryParser import ResourceQueryParser
from .Config import Config
from .SignalDispatcher import SignalDispatcher
from .Mail import Mail
from .version import __version__
from .plugin import instanciate_plugins
from .Scheduler import Scheduler
from .ResourceDbCache import ResourceDbCache

import logging
import sys
import os
import datetime
import pytz


class Core(object):

    __instance = None

    @staticmethod
    def get_instance():
        return Core.__instance

    def __init__(self, config=None):
        self.running = False

        self.config = Config(self, config)

        self._init_logger()
        self._init_database()
        self._init_plugins()

        Core.__instance = self

    @property
    def local_tz (self):
        local_tz = self.config.get('timezone', 'UTC')
        return pytz.timezone(local_tz)

    def _init_logger(self):
        self.log = logging.getLogger('ething')
        self.log.setLevel(
            getattr(logging, self.config['log']['level'].upper(), logging.INFO))

    def _init_plugins(self):
        self.plugins = instanciate_plugins(self)

    def _init_database(self):

        try:
            db_type = self.config.get('db.type', 'sqlite').lower()
            if db_type == 'mongodb':
                db_ctor = MongoDB
            else:
                db_ctor = SQL
            self.log.info('db type: %s' % db_ctor)
            self.db = db_ctor(tz = str(self.local_tz), **self.config['db'])

            self.db.connect()
            self.resource_db_cache = ResourceDbCache(self)
        except:
            raise Exception(
                'unable to connect to the database [%s]' % sys.exc_info()[1])

        self.resourceQueryParser = ResourceQueryParser(tz = str(self.local_tz))

    def stop(self):
        self.log.info("stopping ...")
        self.dispatchSignal('DaemonStopped')
        self.running = False

    @property
    def version(self):
        return __version__

    def destroy(self):

        self.log.info("cleaning for exit")

        self.running = False

        for plugin in self.plugins:
            plugin_name = type(plugin).__name__
            try:
                plugin.unload()
                self.log.info('plugin %s unloaded' % plugin_name)
            except Exception as e:
                self.log.exception("error while unload plugin %s" % plugin_name)

        if hasattr(self, 'db'):
            self.db.disconnect()

    def restart(self):
        self.stop()
        self.restart_flag = True

    def init(self):

        self.log.info("ething %s" % self.version)
        self.log.info("Using home directory: %s" % os.getcwd())

        self.signalDispatcher = SignalDispatcher()
        self.mail = Mail(self)
        self.scheduler = Scheduler()
        
        self.scheduler.at(self._tick, hour='*', min='*')

        # load the plugins
        for plugin in self.plugins:
            plugin_name = type(plugin).__name__
            try:
                plugin.load()
                self.log.info('plugin %s loaded' % plugin_name)
            except Exception:
                self.log.exception('unable to load the plugin %s' % plugin_name)

        self.signalDispatcher.bind('ConfigUpdated', self._on_config_updated)

    def start(self):
        self.init()
        self.running = True
        self.dispatchSignal('DaemonStarted')

    def loop(self, timeout=1):
        self.signalDispatcher.process(timeout)
        self.scheduler.process()

    def loop_forever(self):
        while self.running:
            self.loop(1)
    
    def _tick(self):
        self.dispatchSignal('Tick')

    def _on_config_updated(self, signal):
        update_log = False
        update_notification = False

        for change in signal.changes:
            attr_name = change[0]
            if attr_name.startswith("log."):
                update_log = True
            elif attr_name.startswith("notification."):
                update_notification = True

        if update_log:
            self.log.debug('log config updated')
            self._init_logger()
        if update_notification:
            self.log.debug('notification config updated')
            self.mail = Mail(self)

    #
    # Resources
    #

    def find(self, query=None, limit=None, skip=None, sort=None):

        if query is not None:

            if isinstance(query, string_types) or callable(query):
                query = [query]

            filters = []
            for q in query:
                if isinstance(q, string_types):
                    # expression
                    filters.append(self.resourceQueryParser.compile(q))
                else:
                    filters.append(q)

            def fn(r):
                for f in filters:
                    try:
                        res = f(r)
                    except:
                        res = False
                    if not res:
                        return False
                return True

            query = fn

        return self.resource_db_cache.find(query = query, limit = limit, skip = skip, sort = sort)

    def findOne(self, query=None):
        r = self.find(query, 1)
        return r[0] if len(r) > 0 else None

    def get(self, id):
        if not isinstance(id, string_types):
            raise ValueError('id must be a string')
        return self.resource_db_cache.get(id)

    def create(self, type, attributes):
        cl = get_registered_class(type)
        if cl is not None:
            return cl.create(attributes, ething=self)
        else:
            raise Exception('the type "%s" is unknown' % type)

    def usage(self):
        return {
            'used': self.db.get_usage()
        }

    @staticmethod
    def r_encode(data, showPrivateField=True, local_tz = None):
        o = {}
        for k in data:

            v = data[k]

            if k == '_id':
                k = 'id'

            if k[0] != '_':
                if k[0] == '#':  # show the hidden field (apikey ...)
                    if not showPrivateField:
                        continue
                    k = k[1:]

                if isinstance(v, datetime.datetime):
                    if local_tz is None:
                        local_dt = v
                    else:
                        local_dt = v.replace(tzinfo=pytz.utc).astimezone(local_tz)
                    o[k] = local_dt.isoformat()
                elif isinstance(v, dict):
                    o[k] = Core.r_encode(v)
                else:
                    o[k] = v

        return o

    def dispatchSignal(self, signal, *args, **kwargs):

        if isinstance(signal, string_types):
            try:
                cls = get_registered_class('signals/' + signal)
                if not cls:
                    return
                signal = cls(*args, **kwargs)
            except:
                self.log.exception('signal instanciate error')

        self.signalDispatcher.queue(signal)

        # if hasattr(self, "signalManager"):
        #     self.signalManager.dispatch(signal)

    def notify(self, message, subject = None):

        self.dispatchSignal('Notified', message = message, subject = subject)

        self.mail.send(message = message, subject = subject)

    def reset(self):
        """
        clear all the database !
        """
        self.db.clear()
        self.resource_db_cache.reload()

    def repair(self):
        """
        repair the database
        """
        results = {}

        resources = self.find()

        results['count'] = len(resources)

        i = 0
        n = len(resources)

        for r in resources:
            i += 1
            self.log.info("repairing %d/%d %s %s %s ..." %
                          (i, n, r.type, r.id, r.name))
            r.repair()

        return results

    def get_plugin(self, name):
        for p in self.plugins:
            if p.name == name:
                return p

