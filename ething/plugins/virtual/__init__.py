
from ething.core.scheduler import *
from ething.core.interfaces import *
from ething.core.Resource import Resource, meta
from ething.core.plugin import Plugin
import random
import os


#
# Button, Switch, ...
#

@meta(category="virtual")
class VirtualButton(Button):

    @setInterval(30)
    def _main(self):
        self.click()


@meta(category="virtual")
class VirtualDimmer(Dimmer):

    @setInterval(30)
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
class VirtualRGBLight(RGBLight):
    pass


@meta(category="virtual")
class VirtualRGBWLight(RGBWLight):
    pass


#
# Sensors
#

@meta(category="virtual")
class VirtualThermometer(Thermometer):
    @setInterval(30)
    def _main(self):
        self.temperature = round(random.random() * 30., 2)


@meta(category="virtual")
class VirtualPressureSensor(PressureSensor):
    @setInterval(30)
    def _main(self):
        self.pressure = int(random.random() * 110000.)


@meta(category="virtual")
class VirtualHumiditySensor(HumiditySensor):
    @setInterval(30)
    def _main(self):
        self.humidity = round(random.random() * 100., 1)


@meta(category="virtual")
class VirtualLightSensor(LightSensor):
    @setInterval(30)
    def _main(self):
        self.light_level = round(random.random() * 800., 2)


@meta(category="virtual")
class VirtualMoistureSensor(MoistureSensor):
    @setInterval(30)
    def _main(self):
        self.moisture = round(random.random() * 100., 1)


@meta(category="virtual")
class VirtualAnemometer(Anemometer):
    @setInterval(30)
    def _main(self):
        self.wind_speed = round(random.random() * 40., 2)
        self.wind_direction = int(random.random() * 360.)


@meta(category="virtual")
class VirtualDoorSensor(DoorSensor):
    @setInterval(30)
    def _main(self):
        self.state = random.choice([True, False])


#
# others
#

class VirtualCamera(Camera):

    def snapshot(self):
        with open(os.path.join(os.path.dirname(__file__), 'img.jpg'), mode='rb') as file:  # b is important -> binary
            fileContent = file.read()
        return fileContent



virtual_classes = []

for k in list(locals()):
    v = locals()[k]
    if k.startswith('Virtual') and issubclass(v, Resource):
        virtual_classes.append(v)


class VirtualPlugin(Plugin):

    def setup(self):
        for vcls in virtual_classes:
            if self.core.findOne(vcls) is None:
                self.core.create(vcls, {
                    'name': vcls.__name__
                })



