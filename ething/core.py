# coding: utf-8

from future.utils import string_types
from .db import Db
from .reg import get_registered_class, get_definition_name, update
from .Config import Config
from .version import __version__
from .plugin import search_plugin_cls, import_plugins
from .scheduler import set_interval
from .dispatcher import emit
from .utils import get_info
from .utils.ObjectPath import generate_filter, patch_all
from .Resource import Resource
from .flow import generate_event_nodes
from .env import USER_DIR, LOG_FILE
from .notification import *
from functools import wraps
import collections
import logging
import pytz
import time
import inspect
import threading


DEFAULT_COMMIT_INTERVAL = 5
DEFAULT_GARBAGE_COLLECTOR_PERIOD = 300

LOGGER = logging.getLogger(__name__)



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

    def __init__(self, name=None, debug=False, database=None, clear_db=False, commit_interval=None, garbage_collector_period=None, **plugins_options):
        """

        :param name: the name of the core instance. Default to None.
        :param debug: If True, run the instance in debug mode.
        :param log_level: Any level from the logging module. Default to ``logging.INFO``
        :param clear_db: If True, the database will be cleared.
        :param logger: A logger instance. By default, a new logger instance will be created.
        :param commit_interval: The interval the database will be synchronized. Default to 5sec.
        :param garbage_collector_period: The period after which the database cache will be remove. Default to 300sec.

        .. attribute:: db

            link to the database instance.

            :type: :class:`ething.db.Db`

        """
        self._initialized = False

        patch_all(self)

        self.name = name
        self.plugins = list()
        self.debug = debug

        self.log = LOGGER

        self.log.info('USER_DIR   : %s', USER_DIR)
        self.log.info('LOG_FILE   : %s', LOG_FILE)
        info = get_info(self)
        self.log.info("ETHING     : version=%s", info.get('VERSION'))
        python_info = info.get('python', {})
        self.log.info("PYTHON     : version=%s type=%s",
                    python_info.get('version'), python_info.get('type'))
        self.log.info("PYTHON_EXE : %s", python_info.get('executable'))
        platform_info = info.get('platform', {})
        self.log.info("PLATFORM   : %s", platform_info.get('name'))
        self.log.info("SYSTEM     : %s", platform_info.get('version'))

        self.log.info("DEBUG      : %s", debug)

        # load db
        self._init_database(database, clear_db=clear_db, commit_interval=commit_interval, garbage_collector_period=garbage_collector_period)

        self.config = Config(self)

        self.__instances.append(self)

        plugin_modules = import_plugins()

        generate_event_nodes()

        for p in plugin_modules:
            opt = dict()
            prefix = p.__name__ + '_'
            for k in plugins_options:
                if k.startswith(prefix):
                    opt[k[len(prefix):]] = plugins_options[k]
            self.use(p, **opt)

        # load all resources
        self.db.os[Resource].load()

        # setup plugins
        self._plugins_call('setup')

        # devices activity timeout
        def devices_activity_check():
            for d in self.find(lambda r: r.typeof('resources/Device')):
                d.check_activity()

        set_interval(60, devices_activity_check)

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
                self.log.debug('plugin %s: already loaded', plugin_name)
                return p

        # instanciate:
        try:
            plugin = plugin_cls(self, options)
            plugin.load()
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
            # commit every x secondes
            if commit_interval is None:
                commit_interval = DEFAULT_COMMIT_INTERVAL
            set_interval(commit_interval, self.db.commit, condition=lambda _: self.db.connected and self.db.need_commit())

        # run garbage collector regularly
        if garbage_collector_period is None:
            garbage_collector_period = DEFAULT_GARBAGE_COLLECTOR_PERIOD
        set_interval(garbage_collector_period, self.db.run_garbage_collector, condition=lambda _: self.db.connected)

    @property
    def version(self):
        return __version__

    def close(self):
        self.log.info("close")

        self._plugins_call('unload')

        if hasattr(self, 'db'):
            self.db.disconnect()

    def notify(self, message, mode=INFO, persistant=False, **kwargs):
        return notify(self, message, mode, persistant, **kwargs)

    #
    # Resources
    #

    @property
    def resources(self):
        return self.db.os.find()

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
                    return generate_filter(q, converter=lambda r:r.__json__())
                elif inspect.isclass(q):
                    return lambda r: r.typeof(q)
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

    def find_one(self, query=None):
        """
        Returns only a single resource that optionnaly match a query.

        :param query: Same as find()
        :return: a resource
        """
        r = self.find(query, 1)
        return r[0] if len(r) > 0 else None

    def get(self, id):
        """
        Returns a resource with a given id.

        :param id: a resource id
        :return: a resource
        """
        if not isinstance(id, string_types):
            raise ValueError('id must be a string')
        return self.db.os.get(Resource, id)

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
        return self.db.os.create(cls, attributes)

    def emit(self, signal, *args, **kwargs):
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

        emit(signal, sender=self)

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
            except:
                self.log.exception("plugin %s: error while executing '%s'" % (p.name, method))

