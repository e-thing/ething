# coding: utf-8
from future.utils import string_types
from .Config import ConfigItem
import logging
import inspect
import os
import copy
import pkgutil
import importlib
import pkg_resources
from email.parser import FeedParser


class BasePlugin(object):

    # if this plugin come from a package, this attribute will contain his name
    PACKAGE = None

    # the path to the plugin javascript file (metadata, widgets ...). This file is loaded by the web interface. (default to index.js)
    JS_INDEX = './index.js'

    def __init__(self, core, js_index = None):
        self.core = core
        package = getattr(self, 'PACKAGE', None) or {}
        self._name = package.get('name') or type(self).__name__
        self._js_index = js_index or getattr(self, 'JS_INDEX')

    @property
    def name(self):
        return self._name

    @property
    def js_index(self):
        if os.path.isabs(self._js_index):
            return self._js_index
        # make it absolute !
        package = getattr(self, 'PACKAGE', None) or {}
        root = package.get('location')
        return os.path.normpath(os.path.join(root or os.getcwd(), self._js_index))

    def is_js_index_valid(self):
        return os.path.isfile(self.js_index)

    def __str__(self):
        return '<plugin %s>' % self.name

    def __repr__(self):
        return str(self)

    def load(self):
        pass

    def setup(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def unload(self):
        pass

    def export_data(self):
        pass

    def import_data(self, data):
        pass

    def toJson(self):
        return {
            'name': self.name,
            'package': self.PACKAGE
        }


class Plugin(BasePlugin):

    # a dictionary object defining the default configuration of the plugin
    CONFIG_DEFAULTS = None

    # a json schema describing the configuration data. The web interface use this to create the configuration form
    CONFIG_SCHEMA = None

    def __init__(self, core, js_index=None, config_defaults=None, config_schema=None):
        super(Plugin, self).__init__(core, js_index)

        self._log = getattr(self, 'log', None) or logging.getLogger("ething.%s" % self.name)

        self._config = ConfigItem(core.config, self.name, schema=config_schema or getattr(self, 'CONFIG_SCHEMA'),
                                 defaults=copy.deepcopy(config_defaults or getattr(self, 'CONFIG_DEFAULTS')))

    @property
    def config(self):
        return self._config

    @property
    def log(self):
        return self._log

    def start(self):
        self.core.signalDispatcher.bind('ConfigUpdated', self._on_core_config_updated)

    def on_config_change(self):
        pass

    def stop(self):
        self.core.signalDispatcher.unbind('ConfigUpdated', self._on_core_config_updated)

    def _on_core_config_updated(self, signal):
        if self.name in signal.updated_keys:
            self.on_config_change()

    def toJson(self):
        data = super(Plugin, self).toJson()
        data['config'] = self.config
        return data


def get_package_info(mod):
    package = {}

    if inspect.ismodule(mod):

        name = mod.__name__

        if name.startswith('ething.plugins.'):
            name = name[15:]
            package['builtin'] = True

        package['name'] = name

        if mod.__path__:
            package['location'] = mod.__path__[0]

        if hasattr(mod, '__version__'):
            package['version'] = mod.__version__
        if hasattr(mod, 'version'):
            package['version'] = mod.version

        mod = mod.__name__

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


def install_func_to_plugin(install_func, name = 'AnonymousPlugin'):

    def load(self):
        return install_func(self.core)

    return type(name, (BasePlugin,), {
        'load': load
    })


#class EmptyPlugin(BasePlugin):
#    pass


def extract_plugin_from_module(mod):

    for attr_name in dir(mod):
        attr = getattr(mod, attr_name, None)
        if inspect.isclass(attr) and issubclass(attr, Plugin) and attr is not Plugin:
            return attr
    else:
        install_func = getattr(mod, 'install', None)
        if install_func and callable(install_func):
            return install_func_to_plugin(install_func)

    # raise Exception('module "%s" has no plugin install function found nor plugin class found' % mod)

    # no install found -> EmptyPlugin
    return type('EmptyPlugin', (BasePlugin,), {})


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
        raise ValueError('invalid argument in use()')

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
