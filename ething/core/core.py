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
from .utils.ObjectPath import generate_filter, patch_all
from .Resource import Resource
from .Process import Process, Manager as ProcessManager
from .flow import generate_event_nodes
from functools import wraps
import collections
import logging
import pytz
import time
import inspect
import threading


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


def after_init(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self._initialized:
            raise Exception('Core is not initialized !')
        return f(self, *args, **kwargs)
    return wrapper


class Core(object):
    """

    instantiate a new Core instance::

        core = Core()

    load any plugins here::

        import my_plugin
        core.use(my_plugin)

    run the server::

        core.run()

    """

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

    def __init__(self, name=None, debug=False, log_level=None, database=None, clear_db=False, logger=None, commit_interval=None, garbage_collector_period=None, **config):
        """

        :param name: the name of the core instance. Default to None.
        :param debug: If True, run the instance in debug mode.
        :param log_level: Any level from the logging module. Default to ``logging.INFO``
        :param clear_db: If True, the database will be cleared.
        :param logger: A logger instance. By default, a new logger instance will be created.

        .. attribute:: db

            link to the database instance.

            :type: :class:`ething.core.db.Db`

        """
        self._initialized = False

        patch_all(self)

        self._running = threading.Event()
        self._stop = threading.Event()
        self._stopped = threading.Event()

        self.name = name
        self.plugins = list()
        self.debug = debug

        if log_level is None:
            log_level = logging.DEBUG if debug else logging.INFO

        self.log = logger or logging.getLogger('ething')
        self.log.setLevel(log_level)

        self.signalDispatcher = SignalDispatcher()
        self.process_manager = ProcessManager(start=False)
        self.scheduler = _CoreScheduler(self)

        self.process_manager.attach(Process(name="scheduler", loop=self.scheduler.process, loop_interval=1))
        self.process_manager.attach(Process(name="signalDispatcher", loop=self.signalDispatcher.process, args=(1,)))

        # load db
        self._init_database(database, clear_db=clear_db, commit_interval=commit_interval, garbage_collector_period=garbage_collector_period)

        self.config = Config(self)

        if config:
            with self.config:
                update(self.config, config)

        self.__instances.append(self)

        for p_cls in list_registered_plugins():
            self.use(p_cls)

    @property
    def running(self):
        """True if this instance is running"""
        return self._running.isSet()

    @property
    def local_tz (self):
        local_tz = self.config.timezone
        return pytz.timezone(local_tz)

    def use(self, something, **options):
        """
        Load a plugin.

        :param something: A plugin. Either a Plugin class, a module or an install function.
        :param options: Some paramaters to pass to the plugin.load(...) method.
        :return: The plugin instance.
        """
        if self._initialized:
            raise Exception('unable to use this plugin: the core is already initialized')

        plugin_cls = search_plugin_cls(something)
        plugin_name = plugin_cls.get_name()

        for p in self.plugins:
            if p.name == plugin_name:
                self.log.debug('plugin %s: already loaded' % plugin_name)
                return p

        # instanciate:
        try:
            plugin = plugin_cls(self)
            plugin.load(**options)
        except:
            self.log.exception('plugin %s: unable to load' % plugin_name)
        else:
            self.plugins.append(plugin)

            info = getattr(plugin, 'PACKAGE', None)
            if info:
                info = ', '.join(['%s: %s' % (k, str(info[k])) for k in info])

            self.log.info('plugin %s loaded, info: %s' % (plugin.name, info))
            return plugin

    def _init_database(self, database=None, clear_db=False, commit_interval=None, garbage_collector_period=None):
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

    def stop(self, block=False):
        """
        Stop the core instance.

        :param block: If provided and True, will block until the core instance has really stopped, which can take some time.
        """
        if self._stop.is_set():
            # already stopped
            return

        self.log.info("stopping ...")
        self._stop.set()

        if block:
            self._stopped.wait()

    @property
    def version(self):
        return __version__

    def destroy(self):
        """
        Free up the memory.

        """
        self.log.debug("cleaning for exit...")

        self._plugins_call('unload')

        self.signalDispatcher.clear()
        self.process_manager.clear()
        self.scheduler.clear()

        if hasattr(self, 'db'):
            self.db.disconnect()

        self._initialized = False

    def init(self):
        """
        Initialize the core instance. For testing purpose only. The run() method automatically call this method.

        """
        if not self._initialized:
            self._initialized = True

            generate_event_nodes()

            # preload all resources
            self.db.os[Resource].load()

            # setup plugins
            self._plugins_call('setup')

    def run(self):
        """
        Run the core instance. Block until the stop() method is called.
        Raise an exception if the core is already running.

        """
        if self.running:
            raise Exception('already running')

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

        self.log.info('core started')

        self._running.set()
        self._stop.clear()
        self._stopped.clear()
        self._plugins_call('start')
        self.process_manager.start()

        # wait for stop...
        self._stop.wait()

        self._plugins_call('stop')
        self.process_manager.stop(timeout=2)

        self.log.info('core stopped')

        self._running.clear()
        self._stopped.set()

    #
    # Resources
    #

    @after_init
    def find(self, query=None, limit=None, skip=None, sort=None):
        """
        Return resources.

        :param query: Either a string representing an ObjectPath query expression, or a predicate. If a list of queries is given, returns only resources that match all the queries.
        :param limit: specify the maximum number of returned resources.
        :param skip: The number of resources to skip in the results set.
        :param sort: Specifies the order of the returned resources. Must be a string representing a resource attribute. If preceded by '-', the sort will be descending order.
        :return: A list of resources
        """

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

    @after_init
    def findOne(self, query=None):
        """
        Returns only a single resource that optionnaly match a query.

        :param query: Same as find()
        :return: a resource
        """
        r = self.find(query, 1)
        return r[0] if len(r) > 0 else None

    @after_init
    def get(self, id):
        """
        Returns a resource with a given id.

        :param id: a resource id
        :return: a resource
        """
        if not isinstance(id, string_types):
            raise ValueError('id must be a string')
        return self.db.os.get(Resource, id)

    @after_init
    def create(self, cls, attributes):
        """
        Create a new resource.

        :param cls: Either a string representing a resource type or a resource class.
        :param attributes: A dict containing all the attributes
        :return: a resource
        """
        if isinstance(cls, string_types):
            cls_name = cls
            cls = get_registered_class(cls_name)
            if cls is None:
                raise Exception('the type "%s" is unknown' % cls_name)
        attributes['type'] = get_definition_name(cls)
        return self.db.os.create(Resource, attributes)

    def dispatchSignal(self, signal, *args, **kwargs):
        """
        Dispatch a signal.

        :param signal: Either a signal instance or a string representing a signal type.
        :param args: Only used if a string was provided as signal. Any extra arguments to pass when instantiate the signal.
        :param kwargs: Only used if a string was provided as signal. Any extra arguments to pass when instantiate the signal.
        """
        if isinstance(signal, string_types):
            try:
                if not signal.startswith('signals/'):
                    signal = 'signals/' + signal
                cls = get_registered_class(signal)
                if not cls:
                    raise Exception('unknown signal %s' % signal)
                signal = cls(*args, **kwargs)
            except:
                self.log.exception('signal instantiate error')

        self.signalDispatcher.queue(signal)

    def get_plugin(self, name):
        """
        Find a plugin by its name.

        :param name: the name of the plugin.
        :return: A plugin instance.
        """
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

