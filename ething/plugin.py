# coding: utf-8
from future.utils import string_types
from .reg import *
from .env import get_options, get_env
from .utils import generate_id
from .Config import SettingsUpdated
import logging
import inspect
import os
import pkgutil
import importlib
import pkg_resources
from email.parser import FeedParser
from .plugins import import_builtin_plugins
from .scheduler import bind_instance
from .Signal import Signal
from .dispatcher import SignalEmitter
from .notification import NotificationManager
from .processes import ProcessCollection
from .Signal import PluginSignal


LOGGER = logging.getLogger(__name__)


@meta(icon='mdi-update')
class PluginUpdated(PluginSignal):
    """
    is emitted each time a plugin attribute has been updated
    """
    def __init__(self, plugin, attributes):
        super(PluginUpdated, self).__init__(plugin, attributes=attributes)

    @property
    def attributes(self):
        return self.data['attributes']


def generate_plugin_name(suffix):
    return "%s_%s" % (suffix, generate_id())


class PluginType(String):

    def __init__(self, must_throw=None, **attributes):
        super(PluginType, self).__init__(allow_empty=False, **attributes)
        self.must_throw = must_throw
        if isinstance(self.must_throw, string_types):
            self.must_throw = get_registered_class(self.must_throw)

    def check(self, plugin):
        if self.must_throw:
            signals_thrown_by_plugin = [s.signal for s in list_registered_signals(plugin)]
            signal = self.must_throw
            if signal not in signals_thrown_by_plugin:
                raise ValueError("the plugin %s does not throw the signal : %s" % (
                    plugin.name, get_definition_name(signal)))

    def _get_plugin(self, plugin_typename, context):
        try:
            plugin = context['core'].plugins.get_from_type(plugin_typename)
        except KeyError:
            raise ValueError('the plugin %s does not exist' % plugin_typename)

        return plugin

    def get(self, value, context=None):
        return self._get_plugin(value, context)

    def set(self, value, context=None):
        if isinstance(value, string_types):
            value = super(PluginType, self).set(value, context)
            self.check(self._get_plugin(value, context))
        else: # plugin instance
            self.check(value)
            value = get_definition_name(value)
        return value

    def from_json(self, value, context=None):
        value = super(PluginType, self).from_json(value, context)
        # check the plugin exist !
        self.check(self._get_plugin(value, context))
        return value

    def serialize(self, value, context=None):
        return value

    def to_shema(self, context = None):
        schema = super(PluginType, self).to_shema(context)
        schema['$component'] = 'ething.plugin'
        if self.must_throw:
            schema['$must_throw'] = get_definition_name(self.must_throw)
        return schema


class PluginMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        cls.LOGGER = logging.getLogger('ething.plugins.%s' % cls.get_name())

        return cls


@abstract
@namespace('plugins')
@throw(PluginUpdated)
@meta(description='')
class Plugin(with_metaclass(PluginMetaClass, Entity, SignalEmitter)):
    """
    To create a new plugin, just override this class.

    Example::

        @attr('some_config')
        class MyPlugin(Plugin):

            def setup(self):
                # access the core instance
                self.core

                # access to the registered configuration (note, this config is accessible through the web interface):
                self.some_config

                # access to the command line options
                self.options.get('foo')

    """

    # if this plugin come from a package, this attribute will contain his name
    PACKAGE = dict()

    # the path to the plugin javascript file (metadata, widgets ...). This file is loaded by the web interface. (default to index.js)
    JS_INDEX = './index.js'

    @classmethod
    def get_name(cls):
        return getattr(cls, 'PACKAGE', {}).get('name', cls.__name__)

    def __init__(self, core):
        """

        .. attribute:: core

            link to the core instance.

            :type: :class:`ething.Core`

        """
        self._processes = ProcessCollection(parent=self)
        self._notification = NotificationManager(core, self)

        self.options = get_options(self.name)

        # get the config from the core db
        config = core.db.store.get('config.%s' % self.name, None)

        super(Plugin, self).__init__(config, {
            'core': core
        }, data_src='db')

        bind_instance(self)

    @property
    def processes(self):
        return self._processes

    @property
    def notification(self):
        """
        the notification manager
        """
        return self._notification

    def __transaction_end__(self):
        if is_dirty(self):
            updated_keys = [a.name for a in list_dirty_attr(self)]
            self.on_config_change(updated_keys)

            self.core.db.store['config.%s' % self.name] = serialize(self)
            clean(self)

            LOGGER.info('config updated: %s', updated_keys)

            self.emit(PluginUpdated(self, updated_keys))

    @property
    def name(self):
        """the name of this plugin"""
        return self.get_name()

    @property
    def logger(self):
        """the name of this plugin"""
        return self.LOGGER

    @classmethod
    def js_index(cls):
        _js_index = getattr(cls, 'JS_INDEX', None)
        if os.path.isabs(_js_index):
            return _js_index
        # make it absolute !
        package = getattr(cls, 'PACKAGE', None) or {}
        root = package.get('location')
        return os.path.normpath(os.path.join(root or os.getcwd(), _js_index))

    @classmethod
    def is_js_index_valid(cls):
        return os.path.isfile(cls.js_index())

    def __str__(self):
        return '<plugin %s>' % self.name

    def __repr__(self):
        return str(self)

    def on_config_change(self, dirty_attributes):
        """
        Is called each time an attribute changed.

        :param dirty_attributes: The names of the attributes that changed.
        """
        pass

    def load(self):
        """
        Is called right after this plugin was instanciated.
        """
        pass

    def setup(self):
        """
        Is called once the core instance is initialized (ie by calling core.init() or core.start() )
        """
        pass

    def unload(self):
        """
        Is called once the core has been destroyed. Used to free up the memory.
        """
        pass

    @classmethod
    def __schema__(cls, schema, context=None):
        schema['js_index'] = cls.is_js_index_valid()
        schema['package'] = cls.PACKAGE
        schema['title'] = cls.get_name()
        return schema

    def __json__(self):
        # do not send the options as it may contain some secret information
        j = super(Plugin, self).__json__()
        j['name'] = self.name
        j['type'] = get_definition_name(self)
        return j


def get_package_info(mod):
    package = {}
    name = None

    if isinstance(mod, string_types):
        name = mod

    if inspect.ismodule(mod):

        name = mod.__name__

        if mod.__path__:
            package['location'] = mod.__path__[0]

        if hasattr(mod, '__version__'):
            package['version'] = mod.__version__
        if hasattr(mod, 'version'):
            package['version'] = mod.version

        mod = mod.__name__

    if name is not None:

        if name.startswith('ething.'):
            package['builtin'] = True

        package['name'] = name.split('.').pop()

    try:
        dist = pkg_resources.get_distribution(mod)
    except pkg_resources.DistributionNotFound:
        pass
    else:
        package.update({
            'name': dist.project_name,
            'project_name': dist.project_name,
            'version': dist.version,
            'location': dist.location,
            'requires': [dep.project_name for dep in dist.requires()],
        })

        metadata = None

        if isinstance(dist, pkg_resources.DistInfoDistribution):
            if dist.has_metadata('METADATA'):
                metadata = dist.get_metadata('METADATA')
        else:
            if dist.has_metadata('PKG-INFO'):
                metadata = dist.get_metadata('PKG-INFO')

        feed_parser = FeedParser()
        feed_parser.feed(metadata)
        pkg_info_dict = feed_parser.close()
        for key in ('summary', 'home-page', 'author', 'author-email', 'license'):
            package[key] = pkg_info_dict.get(key)

    if 'location' in package and not os.path.isabs(package['location']):
        package['location'] = os.path.abspath(package['location'])

    return package


def install_func_to_plugin(install_func, name=None):

    def setup(self):
        return install_func(self.core, self.options)

    if name is None:
        name = generate_plugin_name('AnonymousPlugin')

    return type(name, (Plugin,), {
        'setup': setup
    })


def _is_in_module(mod_name, base_mod_name):
    if base_mod_name == mod_name:
        return True
    return (base_mod_name + ".") in mod_name


def extract_plugin_from_module(mod):
    name = mod.__name__.split('.').pop()

    for attr_name in dir(mod):
        attr = getattr(mod, attr_name, None)
        if inspect.isclass(attr) and issubclass(attr, Plugin) and attr is not Plugin and _is_in_module(getattr(attr, '__module__', None), mod.__name__):
            set_meta(attr, 'name', name)
            return attr
    else:
        install_func = getattr(mod, 'install', None)
        if install_func and callable(install_func):
            return install_func_to_plugin(install_func, name)

    # raise Exception('module "%s" has no plugin install function found nor plugin class found' % mod)

    # no install found -> EmptyPlugin
    return type(name or generate_plugin_name('EmptyPlugin'), (Plugin,), {})


def search_plugin_cls(something):
    mod = None
    plugin_cls = None

    if isinstance(something, string_types):
        mod = importlib.import_module(something)
        plugin_cls = extract_plugin_from_module(mod)
    elif inspect.ismodule(something):
        mod = something
        plugin_cls = extract_plugin_from_module(mod)
    elif issubclass(something, Plugin):
        mod = getattr(something, '__module__', None)
        plugin_cls = something
    elif callable(something):
        mod = getattr(something, '__module__', None)
        plugin_cls = install_func_to_plugin(something)
    else:
        raise ValueError('invalid plugin %s' % something)

    # bind plugin meta information
    if not getattr(plugin_cls, 'PACKAGE', None) and mod:
        setattr(plugin_cls, 'PACKAGE', get_package_info(mod))

    return plugin_cls


def find_plugins():
    ret = set()

    # find installed packages in PYTHON_PATH
    for loader, module_name, is_pkg in pkgutil.iter_modules():
        if module_name.startswith('ething_'):
            ret.add(module_name)

    return ret


def import_plugins(white_list=None):
    modules = []

    # disabled plugins
    disabled = set()
    env = get_env()
    for section in env:
        if section != 'core':
            if env[section].get('disable', 'no').lower() in ('y', 'yes', 'true', '1'):
                disabled.add(section)

    # builtin plugins
    modules += import_builtin_plugins(white_list, disabled)

    # installed plugins as package
    for module_name in find_plugins():
        if disabled is None or module_name[7:] not in disabled:
            if white_list is None or module_name[7:] in white_list:
                try:
                    mod = importlib.import_module(module_name)
                    modules.append(mod)
                except:
                    LOGGER.exception('unable to import %s' % module_name)
        else:
            LOGGER.info('plugin %s disabled' % module_name)

    return modules

