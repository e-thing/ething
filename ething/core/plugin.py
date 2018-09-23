from future.utils import with_metaclass
from .Config import Config
import logging
import inspect
import os


class PluginMount(type):
    """plugin metaclass"""

    def __init__(cls, name, bases, attrs):
        """Called when a Plugin derived class is imported"""

        if not hasattr(cls, 'plugins'):
            # Called when the metaclass is first instantiated
            cls.plugins = []
        else:
            # Called when a plugin class is imported
            cls.register_plugin(cls)

    def register_plugin(cls, plugin):
        """Add the plugin to the plugin list and perform any registration logic"""

        if not hasattr(plugin, 'name'):
            plugin.name = cls.__name__

        if hasattr(plugin, 'CONFIG_DEFAULTS'):
            Config.DEFAULT[plugin.name] = plugin.CONFIG_DEFAULTS

        # save the plugin reference
        cls.plugins.append(plugin)

        plugin.register()


class Plugin(with_metaclass(PluginMount, object)):
    """A plugin abstract class"""

    VERSION = None

    def __init__(self, core, **kwargs):
        self.core = core
        self.log = logging.getLogger("ething.%s" % self.name)
        self.config = core.config[self.name] or {}
        self.loaded = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def register(cls):

        # import js index !
        js_index = False
        try:
            file = inspect.getfile(cls)
            js_index_file = os.path.join(os.path.dirname(file), 'index.js')
            if os.path.isfile(js_index_file):
                js_index = js_index_file
        except:
            pass
        cls.js_index = js_index

    def load(self):
        if self.loaded:
            raise Exception('plugin "%s" already loaded' % self)
        self.log.info('load plugin')
        self.core.signalDispatcher.bind('ConfigUpdated', self._on_core_config_updated)
        self.loaded = True

    def unload(self):
        self.core.signalDispatcher.unbind('ConfigUpdated', self._on_core_config_updated)
        self.loaded = False
        self.log.info('unload plugin')

    def on_config_change(self, changes):
        pass

    def _on_core_config_updated(self, signal):

        local_changes = []
        for change in signal.changes:
            attr_name = change[0]
            if attr_name == self.name or attr_name.startswith("%s." % self.name):
                local_changes.append(change)

        if len(local_changes) > 0:
            self.on_config_change(local_changes)


def instanciate_plugins(core, **kwargs):
    plugin_instances = []
    for plugin in Plugin.plugins:
        plugin_instances.append(plugin(core, **kwargs))
    return plugin_instances