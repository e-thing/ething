# coding: utf-8

from ething.Device import *
from ething.interfaces import Thermometer
from ething.plugin import Plugin
from ething.IntervalProcess import IntervalProcess

#import pythoncom
#import wmi
import random


class CPUTempDevice (Device, Thermometer):
    pass


class CPUTempPlugin (Plugin):

    def load(self):
        super(CPUTempPlugin, self).load()
        self.service = Service(self.core)
        self.service.start()

    def unload(self):
        super(CPUTempPlugin, self).unload()
        if hasattr(self, 'service'):
            self.service.stop()
            del self.service


class Service(IntervalProcess):

    def __init__(self, core):
        super(Service, self).__init__('CPUTemp', 30)
        self.core = core

    def begin(self):
        self.device = self.core.findOne({
            'type': 'resources/CPUTempDevice'
        })

        if self.device is None:
            self.log.info('create device')
            self.device = self.core.create('resources/CPUTempDevice', {
                'name': 'CPU thermometer'
            })

        #pythoncom.CoInitialize()

    def process(self):
        #w = wmi.WMI(namespace=r"root\wmi")
        #temperature = (w.MSAcpi_ThermalZoneTemperature()[0].CurrentTemperature / 10) - 273.2
        temperature = round(random.random() * 40., 2)
        self.log.info('read temperature %s on %s' % (temperature, self.device))
        with self.device:
            self.device._temperature = temperature

    def end(self):
        #pythoncom.CoUninitialize()
        pass