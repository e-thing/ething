# coding: utf-8

from future.utils import string_types

from .reg import get_registered_class
from .ResourceQueryParser import ResourceQueryParser
from .Config import CoreConfig
from .SignalDispatcher import SignalDispatcher
from .version import __version__
from .plugin import search_plugin_cls, list_registered_plugins
from .scheduler import Scheduler
from .ResourceDbCache import ResourceDbCache
from .green import mode

import logging
import pytz
import time


class Core(object):
    __instances = []

    @staticmethod
    def get_instance(name=None):
        if name is None:
            if len(Core.__instances) == 1:
                return Core.__instances[0]
        else:
            for instance in Core.__instances:
                if instance.name == name:
                    return instance

    def __init__(self, config=None, name=None):
        self.__initialized = False

        self.running = False
        self.name = name

        self.config = CoreConfig(self, config)

        self._init_logger()

        self.signalDispatcher = SignalDispatcher()
        self.scheduler = Scheduler()

        self.plugins = list()

        self.__instances.append(self)

        for p_cls in list_registered_plugins():
            self.use(p_cls)

    @property
    def local_tz (self):
        local_tz = self.config.get('timezone', 'UTC')
        return pytz.timezone(local_tz)

    def _init_logger(self):
        self.log = logging.getLogger('ething')
        self.log.setLevel(
            getattr(logging, self.config.get('log', {}).get('level', 'info').upper(), logging.INFO))

    def use(self, something):
        plugin_cls = search_plugin_cls(something)
        plugin_name = getattr(plugin_cls, 'PACKAGE', {}).get('name', type(plugin_cls).__name__)

        for p in self.plugins:
            if type(p) is plugin_cls:
                self.log.debug('plugin %s: already loaded' % plugin_name)
                return p

        # instanciate:
        try:
            plugin = plugin_cls(self)
        except:
            self.log.exception('plugin %s: unable to load' % plugin_name)
        else:
            self.plugins.append(plugin)
            plugin.load()

            info = getattr(plugin, 'PACKAGE', None)
            if info:
                info = ', '.join(['%s: %s' % (k, str(info[k])) for k in info])

            self.log.info('plugin %s loaded, info: %s' % (plugin.name, info))
            return plugin

    def _init_database(self, clear_db=False):
        self.resourceQueryParser = ResourceQueryParser(tz=str(self.local_tz))

        try:
            db_type = self.config.get('db.type', 'cached_sqlite').lower()
            if db_type == 'mongodb':
                from .database.mongodb import MongoDB
                db_ctor = MongoDB
            elif db_type == 'unqlite':
                from .database.unqlitedb import UnQLiteDB
                db_ctor = UnQLiteDB
            elif db_type == 'sqlite':
                from .database.sqlite import SQLite
                db_ctor = SQLite
            elif db_type == 'cached_sqlite':
                from .database.cached_sqlite import CachedSQLite
                db_ctor = CachedSQLite
            else:
                raise Exception('unknown db_type %s' % db_type)

            self.log.info('db type: %s' % db_type)
            self.db = db_ctor(self, tz = str(self.local_tz), **(self.config.get('db', {})))

            self.db.connect()

            if clear_db:
                self.log.info('clear db')
                self.db.clear()

            self.db.init()

            db_version = self.db.kv_get('VERSION')
            self.log.info('db version: %s' % (db_version))
            if db_version is None and self.version != 'unknown':
                self.db.kv_set('VERSION', self.version)

            self.is_db_loaded = False
            self.resource_db_cache = ResourceDbCache(self)

        except Exception as e:
            self.log.exception('init database error')
            raise e

    def stop(self, callback = None):
        self.log.info("stopping ...")
        self._plugins_call('stop')
        self.dispatchSignal('DaemonStopped')
        self.running = False

        if callback is not None:
            try:
                callback(self)
            except:
                self.log.exception('stop callback exception')

    @property
    def version(self):
        return __version__

    def destroy(self):

        self.log.info("cleaning for exit")

        self.running = False

        self._plugins_call('unload')

        self.signalDispatcher.clear()
        self.scheduler.clear()

        if hasattr(self, 'db'):
            self.db.disconnect()

        if hasattr(self, 'resource_db_cache'):
            self.resource_db_cache.unload()

        self.__initialized = False

    def restart(self, callback = None):
        self.stop(callback)
        self.restart_flag = True

    def init(self, clear_db=False):
        if not self.__initialized:
            self.__initialized = True

            self.scheduler.at(self._tick, hour='*', min='*', thread=False)
            self.signalDispatcher.bind('ConfigUpdated', self._on_config_updated)

            # load db
            self._init_database(clear_db=clear_db)

            # setup plugins
            self._plugins_call('setup')

            #load the resources from the database
            self.resource_db_cache.load()
            self.is_db_loaded = True

    def start(self):
        self.init()

        if self.config.get('debug') and mode == 'gevent' and not getattr(self, '_gevent_dbg_installed', False):
            from gevent import events, config

            setattr(self, '_gevent_dbg_installed', True)

            config.max_blocking_time = 1.0
            config.monitor_thread = True

            def event_handler(event):
                if isinstance(event, events.EventLoopBlocked):
                    print('DBG: %s' % event)
                    # print(event.greenlet)
                    # print('****')
                    # print(event.info)
                    # print(event.blocking_time)

            events.subscribers.append(event_handler)

        self.running = True
        self._plugins_call('start')
        self.dispatchSignal('DaemonStarted')

    def loop(self, timeout=1):
        self.signalDispatcher.process(timeout)
        self.scheduler.process()

    def loop_forever(self):
        while self.running:
            self.loop(1)

    def run(self):
        self.start()
        self.loop_forever()
        self.stop()
    
    def _tick(self):
        self.dispatchSignal('Tick')

    def _on_config_updated(self, signal):
        for key in signal.updated_keys:
            if key == "log":
                self.log.debug('log config updated')
                self._init_logger()

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
                    except Exception as e:
                        self.log.exception('error in resource filter')
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

    def create(self, cls, attributes):
        if isinstance(cls, string_types):
            cls = get_registered_class(cls)
        if cls is not None:
            return cls.create(attributes, context={'ething': self})
        else:
            raise Exception('the type "%s" is unknown' % type)

    def usage(self):
        return {
            'used': self.db.get_usage()
        }

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

    def _plugins_call(self, method, *args, **kwargs):
        for p in self.plugins:
            try:
                getattr(p, method)(*args, **kwargs)
                if method == 'unload':
                    self.log.info('plugin %s unloaded' % p.name)
            except:
                self.log.exception("plugin %s: error while executing '%s'" % (p.name, method))

