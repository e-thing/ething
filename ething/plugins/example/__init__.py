# coding: utf-8
from ething.Device import *
from ething.plugin import Plugin
from ething.scheduler import set_interval, delay
from ething.interfaces import *

import os
import time


virtual_classes = []

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

        for vcls in virtual_classes:
            if len(self.core.find(vcls)) == 0:
                self.core.create(vcls, {
                    'name': vcls.__name__
                })

        # if len(self.core.find(RandomThermometer)) == 0:
        #     self.core.create(RandomThermometer, {
        #         'name': 'random thermometer'
        #     })
        #
        # if len(self.core.find(RandomOccupencySensor)) == 0:
        #     self.core.create(RandomOccupencySensor, {
        #         'name': 'random occupency sensor'
        #     })
        #
        # if len(self.core.find(NotConnectedDevice)) == 0:
        #     self.core.create(NotConnectedDevice, {
        #         'name': 'not connected device'
        #     })
        #
        # if len(self.core.find(ErrorDevice)) == 0:
        #     self.core.create(ErrorDevice, {
        #         'name': 'device with error'
        #     })

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









class VirtualWirelessDevice (Thermometer):

    @set_interval(60)
    def refresh_nat(self):
        self.battery = random.randint(5, 100)
        self.rlink_quality = random.randint(5, 100)


class VirtualNotConnectedDevice (Thermometer):
    @delay(1)
    def refresh(self):
        self.refresh_connect_state(False)


class VirtualErrorDevice (Thermometer):
    @delay(1)
    def refresh(self):
        self.error = "This is a test. Some error occured"






#
# Button, Switch, ...
#

@meta(category="virtual")
class VirtualButton(Button):

    @set_interval(30)
    def _main(self):
        self.click()


@meta(category="virtual")
class VirtualDimmer(Dimmer):

    @set_interval(30)
    def _main(self):
        self.level = int(random.random() * 100.)


#
# Actuators
#

@meta(category="virtual")
class VirtualRelay(Relay):
    pass


@meta(category="virtual")
class VirtualDimmableRelay(DimmableRelay):
    pass


@meta(category="virtual")
class VirtualLight(Light):
    pass


@meta(category="virtual")
class VirtualDimmableLight(DimmableLight):
    pass


@meta(category="virtual")
class VirtualRGBWLight(RGBWLight):
    pass




#
# Sensors
#

@meta(category="virtual")
class VirtualThermometer(Thermometer):
    @set_interval(30)
    def _main(self):
        self.temperature = round(random.random() * 30., 2)


@meta(category="virtual")
class VirtualPressureSensor(PressureSensor):
    @set_interval(30)
    def _main(self):
        self.pressure = int(random.random() * 110000.)


@meta(category="virtual")
class VirtualHumiditySensor(HumiditySensor):
    @set_interval(30)
    def _main(self):
        self.humidity = round(random.random() * 100., 1)


@meta(category="virtual")
class VirtualLightSensor(LightSensor):
    @set_interval(30)
    def _main(self):
        self.light_level = round(random.random() * 800., 2)


@meta(category="virtual")
class VirtualMoistureSensor(MoistureSensor):
    @set_interval(30)
    def _main(self):
        self.moisture = round(random.random() * 100., 1)


@meta(category="virtual")
class VirtualAnemometer(Anemometer):
    @set_interval(30)
    def _main(self):
        self.wind_speed = round(random.random() * 40., 2)
        self.wind_direction = int(random.random() * 360.)


@meta(category="virtual")
class VirtualDoorSensor(DoorSensor):
    @set_interval(30)
    def _main(self):
        self.state = random.choice([True, False])


@meta(category="virtual")
class VirtualOccupencySensor (OccupencySensor):

    @set_interval(30)
    def refresh(self):
        self.presence = bool(random.getrandbits(1))


#
# others
#

class VirtualCamera(Camera):

    def snapshot(self):
        with open(os.path.join(os.path.dirname(__file__), 'img.jpg'), mode='rb') as file:  # b is important -> binary
            fileContent = file.read()
        return fileContent





for k in list(locals()):
    v = locals()[k]
    if k.startswith('Virtual') and issubclass(v, Resource):
        virtual_classes.append(v)

