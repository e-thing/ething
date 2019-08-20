# coding: utf-8
from future.utils import string_types
from .reg import *
from .utils import ShortId
import logging
import inspect
import os
import pkgutil
import importlib
import pkg_resources
from email.parser import FeedParser


def generate_plugin_name(suffix):
    return "%s_%s" % (suffix, ShortId.generate())


class PluginMetaClass(MetaReg):
    def __new__(meta, name, bases, dct):
        cls = MetaReg.__new__(meta, name, bases, dct)

        cls.LOGGER = logging.getLogger(cls.get_name())

        return cls


@abstract
@namespace('plugins')
class Plugin(with_metaclass(PluginMetaClass, Entity)):
    """
    To create a new plugin, just override this class.

    Example::

        @attr('some_option')
        class MyPlugin(Plugin):

            def setup(self):
                # access the option:
                self.some_option

                # access the core instance
                self.core


        # bind the plugin to a specific core instance :
        core.use(MyPlugin)

        # or register it globally :
        register_plugin(MyPlugin)

    """

    _REGISTER_ = False

    # if this plugin come from a package, this attribute will contain his name
    PACKAGE = dict()

    # the path to the plugin javascript file (metadata, widgets ...). This file is loaded by the web interface. (default to index.js)
    JS_INDEX = './index.js'

    LOGGER = None

    @classmethod
    def get_name(cls):
        return getattr(cls, 'PACKAGE', {}).get('name', cls.__name__)

    def __init__(self, core):
        """

        .. attribute:: core

            link to the core instance.

            :type: :class:`ething.core.Core`

        """
        # get the config from the core db
        config = core.db.store.get('config.%s' % self.name, None)

        super(Plugin, self).__init__(config, {
            'core': core
        }, data_src='db')

    def __transaction_end__(self):
        if is_dirty(self):

            self.on_config_change([a.name for a in list_dirty_attr(self)])

            self.core.db.store['config.%s' % self.name] = serialize(self)
            clean(self)

    @property
    def name(self):
        """the name of this plugin"""
        return self.get_name()

    @property
    def log(self):
        """the logger of this plugin. Every plugin has his own logger."""
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

    def load(self, **options):
        """
        Is called right after this plugin was instanciated.

        Extra options might be passed this way::

            core.use(MyPlugin, foo='bar')
        """
        pass

    def setup(self):
        """
        Is called once the core instance is initialized (ie by calling core.init() or core.start() )
        """
        pass

    def start(self):
        """
        Is called once the core has been started.
        """
        pass

    def stop(self):
        """
        Is called once the core has been stopped.
        """
        pass

    def unload(self):
        """
        Is called once the core has been destroyed. Used to free up the memory.
        """
        pass


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

    def load(self, **options):
        return install_func(self.core, **options)

    if name is None:
        name = generate_plugin_name('AnonymousPlugin')

    return type(name, (Plugin,), {
        'load': load
    })


def _is_in_module(mod_name, base_mod_name):
    if base_mod_name == mod_name:
        return True
    return (base_mod_name + ".") in mod_name

def extract_plugin_from_module(mod):
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name, None)
        if inspect.isclass(attr) and issubclass(attr, Plugin) and attr is not Plugin and _is_in_module(getattr(attr, '__module__', None), mod.__name__):
            return attr
    else:
        install_func = getattr(mod, 'install', None)
        if install_func and callable(install_func):
            return install_func_to_plugin(install_func)

    # raise Exception('module "%s" has no plugin install function found nor plugin class found' % mod)

    # no install found -> EmptyPlugin
    return type(generate_plugin_name('EmptyPlugin'), (Plugin,), {})


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


_plugins_cache = None


def clear_cache():
    global _plugins_cache
    _plugins_cache = None


def find_plugins():
    global _plugins_cache

    if _plugins_cache is None:
        _plugins_cache = []

        # find installed packages in PYTHON_PATH
        for loader, module_name, is_pkg in pkgutil.iter_modules():
            if module_name.startswith('ething_'):
                _plugins_cache.append(module_name)

    return _plugins_cache


_registered_plugins_cls = set()


def register_plugin(something):
    """
    Register the given plugin globally (ie: will be available in any :class:`ething.core.Core` instance).

    :param something: a plugin, module or install function.
    """
    plugin_cls = search_plugin_cls(something)
    _registered_plugins_cls.add(plugin_cls)


def list_registered_plugins():
    return list(_registered_plugins_cls)
