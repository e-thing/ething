# coding: utf-8
from ething.Device import *
from ething.plugin import Plugin
from ething.scheduler import set_interval, delay
from ething.interfaces.thermometer import Thermometer
from ething.interfaces.occupencySensor import OccupencySensor

import time


# note: the name of the plugin is given by the name of the directory and not the name of the plugin class.


# define your plugin here (see plugin.py for more details)
@attr('interval', type=Integer(min=1), default=300, description="interval in second between 2 log print")
class Example(Plugin):
    # the path of your Javascript index file, this file describe how your plugin should be integrated into the web interface.
    # remove it if not used
    JS_INDEX = './js/index.js'

    # this method is executed once, after the core instance is initialized (database, ...)
    def setup(self):

        # -> access to the static options coming from the ething ini file (located in ~/.ething/conf.ini)
        # the options is a dictionary containing options that are not meant to be changed during runtime.
        # note: the value will be a string, so if you are waiting for number, don't forget to parse it !
        name = self.options.get('name', 'human')
        self.logger.info('hello %s' % name)

        # -> access to the registered configuration
        # the configuration is defined at the top of the plugin using the @attr decorator.
        # note: this config is accessible through the web interface
        # note: this configuration are persistent (stored into the database)
        self.logger.info('interval = %d' % self.interval)

        # if you need to install a background process (see processes.py for more details)
        # or make anything async
        self.processes.add(self.background_process)

        # if no device has been yet created, create one :
        if len(self.core.find(RandomThermometer)) == 0:
            self.core.create(RandomThermometer, {
                'name': 'random thermometer'
            })

        if len(self.core.find(RandomOccupencySensor)) == 0:
            self.core.create(RandomOccupencySensor, {
                'name': 'random occupency sensor'
            })

        if len(self.core.find(NotConnectedDevice)) == 0:
            self.core.create(NotConnectedDevice, {
                'name': 'not connected device'
            })

        if len(self.core.find(ErrorDevice)) == 0:
            self.core.create(ErrorDevice, {
                'name': 'device with error'
            })

        if len(self.core.find(lambda r: r.typeof('resources/File') and r.name == "example_file.txt")) == 0:
            f = self.core.create('resources/File', {
                'name': 'example_file.txt'
            })
            f.write("hello world !")


    # see the setup function
    def background_process (self):
        while (True):
            # do something
            self.logger.debug('hello')
            time.sleep(self.interval)

    def on_config_change(self, dirty_attributes):
        # is called each time the configuration change
        self.logger.info('interval = %d' % self.interval)


#
# you may want to define some devices
# -> a device may be a sensor, a light, a camera ... , the type of the device is given through inheritance
#    generic interface are already defined in the interfaces directory.
#    note: a device may inherit of multiple interfaces (thermometer + humiditySensor).
# -> a device may have attributes (sensor value, light state ...)
#    these attributes must be defined at the top of the class using the @attr decorator, see the interfaces/swith.py file.
#    note: device class inherits from inherited interfaces.
# -> a device may be controlled through methods (turn on, ...)
#    a method is defined using @method decorator. See the interfaces/relay.py file.
#
class RandomThermometer (Thermometer):

    # set_interval is a utility function that execute automatically a method periodically (see scheduler.py)
    @set_interval(30)
    def refresh(self):
        self.temperature = random.randint(-10, 40)



class RandomOccupencySensor (OccupencySensor):

    @set_interval(30)
    def refresh(self):
        self.presence = bool(random.getrandbits(1))

    @set_interval(60)
    def refresh_nat(self):
        self.battery = random.randint(5, 100)
        self.rlink_quality = random.randint(5, 100)


class NotConnectedDevice (Thermometer):
    @delay(1)
    def refresh(self):
        self.refresh_connect_state(False)

class ErrorDevice (Thermometer):
    @delay(1)
    def refresh(self):
        self.error = "<test> some error occured"




