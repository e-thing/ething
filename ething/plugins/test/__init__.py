# coding: utf-8

from ething.core.Device import *
from ething.core.interfaces import Thermometer
from ething.core.plugin import Plugin
from ething.core.IntervalProcess import IntervalProcess

import random


class RandomThermometer (Device, Thermometer):
    pass


class TestPlugin (Plugin):

    def load(self):
        super(TestPlugin, self).load()
        self.service = Service(self.core)
        self.service.start()

    def unload(self):
        super(TestPlugin, self).unload()
        if hasattr(self, 'service'):
            self.service.stop()
            del self.service


class Service(IntervalProcess):

    def __init__(self, core):
        super(Service, self).__init__('Test', 30)
        self.core = core

    def begin(self):
        self.device = self.core.findOne(lambda r: r.isTypeof(RandomThermometer))

        if self.device is None:
            self.log.info('create device')
            self.device = self.core.create(RandomThermometer, {
                'name': 'Random thermometer'
            })

    def process(self):
        temperature = round(random.random() * 40., 2)
        self.log.info('read temperature %s on %s' % (temperature, self.device))
        with self.device:
            self.device._temperature = temperature

    def end(self):
        pass