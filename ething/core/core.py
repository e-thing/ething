# coding: utf-8

from future.utils import string_types
from .db import Db
from .reg import get_registered_class, get_definition_name
from .Config import CoreConfig
from .SignalDispatcher import SignalDispatcher
from .version import __version__
from .plugin import search_plugin_cls, list_registered_plugins
from .scheduler import Scheduler
from .green import mode
from .Signal import Signal
from .utils.objectpath import generate_filter, patch_all
from .Resource import Resource
from .Process import Process, Manager as ProcessManager

import logging
import pytz
import time


class _CoreScheduler(Scheduler):
    def __init__(self, core):
        super(_CoreScheduler, self).__init__()
        self.core = core

    def execute(self, task):
        if not task.allow_multiple:
            if hasattr(task, '_p'):
                p = self.core.process_manager.get(task._p)
                if p and p.is_running:
                    self.log.debug('task "%s" already running: skipped' % task.name)
                    return

        task._p = self.core.process_manager.attach(Process(name=task.name, target=task.target, args=task.args, kwargs=task.kwargs, parent=task.instance)).id


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

        patch_all(self)

        self.running = False
        self.name = name

        self.config = CoreConfig(self, config)

        self._init_logger()

        self.signalDispatcher = SignalDispatcher()
        self.process_manager = ProcessManager(start=False)
        self.scheduler = _CoreScheduler(self)

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
        try:
            db_conf = self.config.get('db', {})
            db_type = db_conf.get('db.type', 'sqlite').lower()

            self.log.info('db type: %s' % (db_type))

            if db_type == 'sqlite':
                from .database.sqlite import SQLiteDriver
                driver = SQLiteDriver(database=db_conf.get('database', 'database'))
            else:
                raise Exception('unknown db_type %s' % db_type)

            self.db = Db(driver, auto_commit=False, cache_delay=3600, auto_connect=True)

            self.db.os.context.update({'core': self})

            if clear_db:
                self.log.info('clear db')
                self.db.clear()

            db_version = self.db.store.get('VERSION')
            self.log.info('db version: %s' % (db_version))
            if db_version is None and self.version != 'unknown':
                self.db.store['VERSION'] = self.version

            if not self.db.auto_commit:
                # commit every secondes
                self.scheduler.setInterval(db_conf.get('commit_interval', 1), self.db.commit, condition=lambda _: self.db.connected and self.db.need_commit())

            # run garbage collector regularly
            self.scheduler.setInterval(300, self.db.run_garbage_collector, condition=lambda _: self.db.connected)

            # preload all resources
            self.db.os[Resource].load()

        except Exception as e:
            self.log.exception('init database error')
            raise e

    def stop(self, callback = None):
        self.log.info("stopping ...")
        self.running = False
        self._plugins_call('stop')
        self.process_manager.stop(timeout=2)

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
        self.process_manager.clear()
        self.scheduler.clear()

        if hasattr(self, 'db'):
            self.db.disconnect()

        self.__initialized = False

    def restart(self, callback = None):
        self.stop(callback)
        self.restart_flag = True

    def init(self, clear_db=False):
        if not self.__initialized:
            self.__initialized = True

            self.signalDispatcher.bind('ConfigUpdated', self._on_config_updated)

            # load db
            self._init_database(clear_db=clear_db)

            # setup plugins
            self._plugins_call('setup')

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
        self.process_manager.start()

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
                    filters.append(generate_filter(q, converter=lambda r:r.toJson()))
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

        return self.db.os.find(Resource, query = query, limit = limit, skip = skip, sort = sort)

    def findOne(self, query=None):
        r = self.find(query, 1)
        return r[0] if len(r) > 0 else None

    def get(self, id):
        if not isinstance(id, string_types):
            raise ValueError('id must be a string')
        return self.db.os.get(Resource, id)

    def create(self, cls, attributes):
        if isinstance(cls, string_types):
            cls_name = cls
            cls = get_registered_class(cls_name)
            if cls is None:
                raise Exception('the type "%s" is unknown' % cls_name)
        attributes['type'] = get_definition_name(cls)
        return self.db.os.create(Resource, attributes)

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

