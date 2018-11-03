from future.utils import with_metaclass
from .Config import ConfigItem
from .Helpers import topological_sort
import logging
import inspect
import os
import json
import copy
from io import open
import traceback
import pkgutil
import importlib


class PluginMount(type):
    """plugin metaclass"""

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""

        if name == 'BuiltinPlugin' or name == 'Plugin':
            return

        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = []
        else:
            # Called when a plugin class is imported
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        """Add the plugin to the plugin list and perform any registration logic"""

        if not plugin.NAME:
            plugin.NAME = cls.__name__

        if not plugin.DESCRIPTION:
            plugin.DESCRIPTION = (plugin.__doc__ or '').strip()

        plugin.register()

        # save the plugin reference
        cls.plugins.append(plugin)




class BasePlugin(with_metaclass(PluginMount, object)):
    """A plugin abstract class"""

    # the name of the plugin (default to the plugin class name)
    NAME = None

    # the version of the plugin
    VERSION = None

    # a string describing this plugin (default to the doc string of this class)
    DESCRIPTION = None

    # a dictionary object defining the default configuration of the plugin
    CONFIG_DEFAULTS = None

    # a json schema describing the configuration data. The web interface use this to create the configuration form
    CONFIG_SCHEMA = None

    # the path to the plugin javascript file (metadata, widgets ...). This file is loaded by the web interface.
    JS_INDEX = None

    # a list of other plugins that need to be loaded before this plugin
    DEPENDENCIES = None

    def __init__(self, core, **kwargs):
        self.core = core
        self.log = logging.getLogger("ething.%s" % self.name)

        self.config = ConfigItem(core.config, self.name, schema = self.CONFIG_SCHEMA, defaults = copy.deepcopy(self.CONFIG_DEFAULTS))

        self.loaded = False

    @property
    def name(self):
        return self.NAME

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def register(cls):

        root_dir = os.path.dirname(inspect.getfile(cls))

        plugin_info = {
            'ui': './index.js',
            'version': None,
            'description': None,
            'name': None,
            'config': None,
            'configSchema': None,
            'dependencies': []
        }

        # read plugin information stored in the json file 'plugin.json'
        try:
            plugin_json_file = os.path.join(root_dir, 'plugin.json')
            if os.path.isfile(plugin_json_file):
                with open(plugin_json_file) as f:
                    plugin_info.update(json.load(f))
        except:
            pass

        if plugin_info.get('name'):
            cls.NAME = plugin_info.get('name')

        if plugin_info.get('ui'):
            js_index_file = os.path.join(root_dir, plugin_info.get('ui'))
            if os.path.isfile(js_index_file):
                cls.JS_INDEX = js_index_file

        if plugin_info.get('version') is not None:
            cls.VERSION = plugin_info.get('version')

        if plugin_info.get('description'):
            cls.DESCRIPTION = plugin_info.get('description')

        if plugin_info.get('config'):
            cls.CONFIG_DEFAULTS = plugin_info.get('config')

        if plugin_info.get('configSchema'):
            cls.CONFIG_SCHEMA = plugin_info.get('configSchema')

        if plugin_info.get('dependencies'):
            cls.DEPENDENCIES = plugin_info.get('dependencies', [])

        cls.ROOT_DIR = root_dir

    def load(self):
        if self.loaded:
            raise Exception('plugin "%s" already loaded' % self)
        self.loaded = True
        self.log.info('load plugin version=%s' % str(self.VERSION))
        self.core.signalDispatcher.bind('ConfigUpdated', self._on_core_config_updated)

    def unload(self):
        self.core.signalDispatcher.unbind('ConfigUpdated', self._on_core_config_updated)
        self.loaded = False
        self.log.info('unload plugin')

    def on_config_change(self):
        pass

    def _on_core_config_updated(self, signal):
        if self.name in signal.updated_keys:
            self.on_config_change()

    def export_data(self):
        pass

    def import_data(self, data):
        pass


def instanciate_plugins(core, **kwargs):
    plugin_instances = []

    plugins_dep = []

    for plugin in BasePlugin.plugins:
        plugins_dep.append((plugin.NAME, plugin.DEPENDENCIES or []))

    ordered = list(topological_sort(plugins_dep))

    for plugin_name in ordered:
        for plugin in BasePlugin.plugins:
            if plugin.NAME == plugin_name:
                try:
                    plugin_instances.append(plugin(core, **kwargs))
                except:
                    core.log.exception('unable to instanciate plugin "%s"' % plugin.NAME)
                break

    return plugin_instances


class BuiltinPlugin(BasePlugin):
    pass


class Plugin(BasePlugin):
    pass


def import_from_path(path):
    for loader, module_name, is_pkg in pkgutil.iter_modules(path):
        try:
            module = loader.find_module(module_name).load_module(module_name)
        except Exception as e:
            print('plugin "%s" import failed: %s' % (module_name, str(e)))
            traceback.print_exc()
        #else:
        #    globals()[module_name] = module

def import_from_package(package):
    pkg = importlib.import_module(package)
    for loader, module_name, is_pkg in pkgutil.iter_modules(pkg.__path__):
        try:
            importlib.import_module('.%s' % module_name, package)
        except Exception as e:
            print('plugin "%s" import failed: %s' % (module_name, str(e)))
            traceback.print_exc()

def import_from_modules():
    for loader, module_name, is_pkg in pkgutil.iter_modules():
        if module_name.startswith('ething_plugin_'):
            try:
                module = loader.find_module(module_name).load_module(module_name)
            except Exception as e:
                print('plugin "%s" import failed: %s' % (module_name, str(e)))
                traceback.print_exc()
