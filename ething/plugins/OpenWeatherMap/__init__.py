# coding: utf-8

from ething.core.plugin import Plugin
from ething.core.IntervalProcess import IntervalProcess
from ething.core.Device import *
from ething.core.interfaces import Thermometer, PressureSensor, HumiditySensor, Anemometer
from ething.core.Resource import ResourceUpdated
from ething.core.interfaces.sensor import SensorValueChanged
import requests
import json

version = '0.1.0'

api_weather_url = 'http://api.openweathermap.org/data/2.5/weather'

refresh_interval = 300 # in seconds


class OpenWeatherMapPlugin(Plugin):

    """
    OpenWeatherMap plugin. Allow you to get the weather for any city.
    """

    VERSION = version

    CONFIG_DEFAULTS = {
        'appid': '',
    }

    CONFIG_SCHEMA = {
        'type': 'object',
        'properties': OrderedDict([
            ('appid', {
                'description': 'Your API ID from OpenWeatherMap. See https://openweathermap.org/appid .',
                'type': 'string'
            })
        ])
    }

    def load(self):
        super(OpenWeatherMapPlugin, self).load()

        self.core.signalDispatcher.bind('ResourceCreated ResourceDeleted ResourceUpdated', self.on_resource_event)

        self.start_process()

    def unload(self):
        super(OpenWeatherMapPlugin, self).unload()
        self.stop_process()

    def start_process(self):
        if self.config.get('appid') and self.has_devices():
            self.process = OpenWeatherMapService(self.core, self.config)
            self.process.start()

    def stop_process(self):
        if hasattr(self, 'process'):
            self.process.stop()
            del self.process

    def restart_process(self):
        self.stop_process()
        self.start_process()

    #def on_config_change(self, changes):
    #    self.restart_process()

    def on_resource_event(self, signal):
        device = signal.resource
        if isinstance(device, OpenWeatherMapDevice):
            if (not isinstance(signal, ResourceUpdated)) or ('location' in signal.attributes):
                self.restart_process()

    def has_devices(self):
        return len(self.core.find(lambda d: isinstance(d, OpenWeatherMapDevice))) > 0


@attr('weather', type=String(), mode=READ_ONLY, default='', history = True, watch = True, description='a string descibing the current weather')
@attr('location', type=String(allow_empty=False), default=NO_VALUE, description='a city\'s name. See https://openweathermap.org/find')
class OpenWeatherMapDevice(Device, Thermometer, PressureSensor, HumiditySensor, Anemometer):

    def _watch(self, attr, new_value, old_value):
        super(OpenWeatherMapDevice, self)._watch(attr, new_value, old_value)

        if attr == 'weather':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))


class OpenWeatherMapService(IntervalProcess):

    def __init__(self, core, config):
        super(OpenWeatherMapService, self).__init__('OpenWeatherMap', refresh_interval)
        self.core = core
        self.config = config

    def process(self):
        self.refresh()

    def refresh(self):
        for device in self.core.find(lambda d: isinstance(d, OpenWeatherMapDevice)):
            try:
                self.refresh_one_device(device)
            except:
                self.log.exception('error fetching data for device %s' % device)

    def refresh_one_device(self, device):
        location = device.location
        appid = self.config.get('appid')
        if location and appid:
            self.log.debug('fetch weather data for %s' % device)
            r = requests.get(url=api_weather_url, params=dict(q=location, APPID=appid, units='metric'))
            r.raise_for_status()
            data = r.json()
            if data:
                with device:
                    device.setConnectState(True)

                    self.log.debug('data read for %s: %s' % (device, json.dumps(data)))

                    main = data.get('main', {})

                    if 'temp' in main:
                        device._temperature = main.get('temp')
                    if 'pressure' in main:
                        device._pressure = main.get('pressure') * 100
                    if 'humidity' in main:
                        device._humidity = main.get('humidity')

                    weather = data.get('weather', [])

                    if len(weather) > 0:
                        weather = weather[0]
                        if isinstance(weather, dict):
                            device._weather = weather.get('description', '')

                    if 'wind' in data:
                        wind = data.get('wind', {})

                        if 'speed' in wind:
                            device._wind_speed = wind.get('speed')
                            device._wind_direction = wind.get('deg', None)


