from future.utils import with_metaclass
import logging


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

        # save the plugin reference
        cls.plugins.append(plugin)

        plugin.register()


class Plugin(with_metaclass(PluginMount, object)):
    """A plugin abstract class"""

    def __init__(self, core, **kwargs):
        self.core = core
        self.log = logging.getLogger(self.__class__.__name__)

    @classmethod
    def register(cls):
        pass

    def load(self):
        pass

    def unload(self):
        pass


def instanciate_plugins(core, **kwargs):
    plugin_instances = []
    for plugin in Plugin.plugins:
        plugin_instances.append(plugin(core, **kwargs))
    return plugin_instances
