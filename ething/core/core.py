# coding: utf-8

from future.utils import string_types
from .db import Db
from .reg import get_registered_class, get_definition_name, update
from .Config import Config
from .SignalDispatcher import SignalDispatcher
from .version import __version__
from .plugin import search_plugin_cls, list_registered_plugins
from .scheduler import Scheduler
from .Signal import Signal
from .utils.objectpath import generate_filter, patch_all
from .Resource import Resource
from .Process import Process, Manager as ProcessManager
from .flow import generate_event_nodes
import collections
import logging
import pytz
import time
import inspect


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

    def __init__(self, name=None, debug=False, log_level=None, database=None, clear_db=False, **config):
        self.__initialized = False

        patch_all(self)

        self.running = False
        self.name = name
        self.plugins = list()
        self.debug = debug

        self._init_logger(log_level)

        self.signalDispatcher = SignalDispatcher()
        self.process_manager = ProcessManager(start=False)
        self.scheduler = _CoreScheduler(self)

        # load db
        self._init_database(database, clear_db=clear_db)

        self.config = Config(self)

        if config:
            with self.config:
                update(self.config, config)

        self.__instances.append(self)

        for p_cls in list_registered_plugins():
            self.use(p_cls)

    @property
    def local_tz (self):
        local_tz = self.config.timezone
        return pytz.timezone(local_tz)

    def _init_logger(self, log_level=None):
        self.log = logging.getLogger('ething')
        if log_level is None:
            log_level = logging.INFO
        self.log.setLevel(log_level)

    def use(self, something):
        plugin_cls = search_plugin_cls(something)
        plugin_name = plugin_cls.get_name()

        for p in self.plugins:
            if p.name == plugin_name:
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

    def _init_database(self, database=None, clear_db=False, commit_interval=None, garbage_collector_period=None):
        try:
            if database is None:
                database = 'database'

            db_type = 'sqlite'

            self.log.info('db type: %s' % (db_type))

            if db_type == 'sqlite':
                from .database.sqlite import SQLiteDriver
                driver = SQLiteDriver(database=database)
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
                if commit_interval is None:
                    commit_interval = 1
                self.scheduler.setInterval(commit_interval, self.db.commit, condition=lambda _: self.db.connected and self.db.need_commit())

            # run garbage collector regularly
            if garbage_collector_period is None:
                garbage_collector_period = 300
            self.scheduler.setInterval(garbage_collector_period, self.db.run_garbage_collector, condition=lambda _: self.db.connected)

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

    def init(self):
        if not self.__initialized:
            self.__initialized = True

            generate_event_nodes()

            # preload all resources
            self.db.os[Resource].load()

            # setup plugins
            self._plugins_call('setup')

    def start(self):
        self.init()

        if self.debug and not getattr(self, '_gevent_dbg_installed', False):
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

    #
    # Resources
    #

    def find(self, query=None, limit=None, skip=None, sort=None):

        if query is not None:

            if not isinstance(query, collections.Sequence):
                query = [query]

            def _mapper(q):
                if isinstance(q, string_types):
                    # expression
                    return generate_filter(q, converter=lambda r:r.toJson())
                elif inspect.isclass(q):
                    return lambda r: r.isTypeof(q)
                else:
                    return q

            filters = list(map(_mapper, query))

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

