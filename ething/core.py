# coding: utf-8

from future.utils import string_types
from .db import Db
from .reg import get_registered_class, get_definition_name
from .Config import Config
from .version import __version__
from .plugin import search_plugin_cls, import_plugins
from .scheduler import set_interval, global_instance as scheduler_instance
from .dispatcher import SignalEmitter
from .processes import ProcessCollection
from .utils import get_info
from .utils.ObjectPath import generate_filter, patch_all
from .Resource import Resource
from .flow import generate_event_nodes
from .env import USER_DIR, LOG_FILE, CONF_FILE, get_options
from .notification import NotificationManager
from .Signal import Signal
from .discovery.ble import start_pairing, stop_pairing
import collections
import logging
import pytz
import inspect
import sys
import time

DEFAULT_COMMIT_INTERVAL = 5

LOGGER = logging.getLogger(__name__)


class _PluginCollection(collections.abc.Mapping):

    def __init__(self, core):
        self._plugins = core._plugins

    def __iter__(self):
        return iter(self._plugins)

    def __getitem__(self, key):
        """
        the key can either be a plugin instance or a plugin name
        """
        for p in self._plugins:
            if p == key or p.name == key:
                return p
        raise KeyError

    def __len__(self):
        return len(self._plugins)

    def get_from_type(self, typename):
        for p in self._plugins:
            if get_definition_name(p) == typename:
                return p
        raise KeyError

    async def call(self, method, *args, **kwargs):
        for p in self._plugins:
            try:
                await getattr(p, method)(*args, **kwargs)
            except:
                LOGGER.exception("plugin %s: error while executing '%s'" % (p.name, method))


class PairingUpdated(Signal):
    """
    Is emitted each time the pairing status changed.
    """

    def __init__(self, state):
        super(PairingUpdated, self).__init__(state=state)


class Core(SignalEmitter):
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

    def __init__(self, name=None, debug=False, database=None, clear_db=False, commit_interval=None,
                 plugins=True, **plugins_options):
        """

        :param name: the name of the core instance. Default to None.
        :param debug: If True, run the instance in debug mode.
        :param log_level: Any level from the logging module. Default to ``logging.INFO``
        :param clear_db: If True, the database will be cleared.
        :param logger: A logger instance. By default, a new logger instance will be created.
        :param commit_interval: The interval the database will be synchronized. Default to 5sec.

        .. attribute:: db

            link to the database instance.

            :type: :class:`ething.db.Db`

        """
        patch_all(self)

        self.name = name
        self._pairing = False
        self._plugins = list()
        self._plugins_coll = _PluginCollection(self)
        self.debug = debug

        self._processes = ProcessCollection(parent=self, weak=True)

        LOGGER.info('CLI_ARGS   : %s', ' '.join(sys.argv[1:]))
        LOGGER.info('USER_DIR   : %s', USER_DIR)
        LOGGER.info('LOG_FILE   : %s', LOG_FILE)
        LOGGER.info('CONF_FILE   : %s', CONF_FILE)
        info = get_info(self)
        LOGGER.info("ETHING     : version=%s", info.get('VERSION'))
        python_info = info.get('python', {})
        LOGGER.info("PYTHON     : version=%s type=%s",
                    python_info.get('version'), python_info.get('type'))
        LOGGER.info("PYTHON_EXE : %s", python_info.get('executable'))
        platform_info = info.get('platform', {})
        LOGGER.info("PLATFORM   : %s", platform_info.get('name'))
        LOGGER.info("SYSTEM     : %s", platform_info.get('version'))

        LOGGER.info("DEBUG      : %s", debug)

        # load db
        self._init_database(database, clear_db=clear_db, commit_interval=commit_interval)

        self.config = Config(self)

        self._notification = NotificationManager(self)

        self.__instances.append(self)

        plugin_modules = import_plugins(None if plugins is True else plugins) if plugins else list()

        generate_event_nodes()

        # todo: parallelise
        for p in plugin_modules:
            await self.use(p)

        # load all resources
        await self.db.os[Resource].load()

        # setup plugins
        await self._plugins_coll.call('setup')

        # start the scheduler
        scheduler_instance().start()

        # devices activity timeout
        def devices_activity_check():
            for d in self.find(lambda r: r.typeof('resources/Device')):
                d.check_activity()

        set_interval(60, devices_activity_check)

        def pairing_update():
            if self.is_pairing:
                pairing_timeout = int(get_options().get('pairing_timeout', 60))
                if pairing_timeout and (time.time() - self._pairing) > pairing_timeout:
                    self.stop_pairing()

        set_interval(5, pairing_update)

    @property
    def local_tz(self):
        local_tz = self.config.timezone
        return pytz.timezone(local_tz)

    @property
    def processes(self):
        """
        the processes collection bind to this instance
        """
        return self._processes

    @property
    def plugins(self):
        """
        the collection of plugins
        """
        return self._plugins_coll

    @property
    def notification(self):
        """
        the notification manager
        """
        return self._notification

    async def use(self, something):
        """
        Load a plugin.

        :param something: A plugin. Either a Plugin class, a module or an install function.
        :return: The plugin instance.
        """

        plugin_cls = search_plugin_cls(something)
        plugin_name = plugin_cls.get_name()

        for p in self._plugins:
            if p.name == plugin_name:
                LOGGER.debug('plugin %s: already loaded', plugin_name)
                return p

        # instanciate:
        try:
            plugin = plugin_cls(self)
            await plugin.load()
        except:
            LOGGER.exception('plugin %s: unable to load' % plugin_name)
        else:
            self._plugins.append(plugin)

            info = getattr(plugin, 'PACKAGE', None)
            if info:
                info = ', '.join(['%s: %s' % (k, str(info[k])) for k in info])

            LOGGER.info('plugin %s loaded, info: %s' % (plugin.name, info))
            return plugin

    async def _init_database(self, database=None, clear_db=False, commit_interval=None):
        if database is None:
            database = 'database'

        db_type = 'sqlite'

        LOGGER.info('db type: %s' % (db_type))

        if db_type == 'sqlite':
            from .database.sqlite import SQLiteDriver
            driver = SQLiteDriver(database=database)
        else:
            raise Exception('unknown db_type %s' % db_type)

        self.db = Db(driver, auto_commit=False, cache_delay=3600)
        await self.db.connect()

        self.db.os.context.update({'core': self})

        await self.db.os.load(Resource)

        if clear_db:
            LOGGER.info('clear db')
            self.db.clear()

        db_version = self.db.store.get('VERSION')
        LOGGER.info('db version: %s' % (db_version))
        if db_version is None and self.version != 'unknown':
            self.db.store['VERSION'] = self.version

        if not self.db.auto_commit:
            # commit every x secondes
            if commit_interval is None:
                commit_interval = DEFAULT_COMMIT_INTERVAL
            set_interval(commit_interval, self.db.commit,
                         condition=lambda _: self.db.connected and self.db.need_commit())

    @property
    def version(self):
        return __version__

    async def stop(self):
        LOGGER.info("stopping...")

        await self._plugins_coll.call('unload')

        # stop the scheduler
        scheduler_instance().stop()

        if hasattr(self, 'db'):
            await self.db.disconnect()

    def start_pairing(self):
        if not self._pairing:
            self._pairing = time.time()
            LOGGER.info('start pairing')
            start_pairing()
            self.emit(PairingUpdated(self.is_pairing))

    def stop_pairing(self):
        if self._pairing:
            stop_pairing()
            self._pairing = False
            LOGGER.info('stop pairing')
            self.emit(PairingUpdated(self.is_pairing))

    @property
    def is_pairing(self):
        return bool(self._pairing)

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

            if not isinstance(query, collections.abc.Sequence):
                query = [query]

            def _mapper(q):
                if isinstance(q, string_types):
                    # expression
                    return generate_filter(q, converter=lambda r: r.__json__())
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
                        LOGGER.exception('error in resource filter')
                        res = False
                    if not res:
                        return False
                return True

            query = fn

        return self.db.os.find(Resource, query=query, limit=limit, skip=skip, sort=sort)

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
