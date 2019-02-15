# coding: utf-8

from ething.core.plugin import Plugin
from ething.core import scheduler
from ething.core.Device import *
from ething.core.interfaces import Thermometer, PressureSensor, HumiditySensor, Anemometer
from ething.core.interfaces.sensor import SensorValueChanged
import requests
import json


API_WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'

REFRESH_INTERVAL = 300 # in seconds


class OpenWeatherMapPlugin(Plugin):

    """
    OpenWeatherMap plugin. Allow you to get the weather for any city.
    """

    JS_INDEX = './js/index.js'

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

    def setup(self):
        if not self.config.get('appid'):
            self.log.warning('no appid set in the configuration')

    def on_config_change(self):
        if not self.config.get('appid'):
            self.log.warning('no appid set in the configuration')


@attr('weather', type=String(), mode=READ_ONLY, default='', history = True, watch = True, description='a string descibing the current weather')
@attr('location', type=String(allow_empty=False), default=NO_VALUE, description='a city\'s name. See https://openweathermap.org/find')
class OpenWeatherMapDevice(Device, Thermometer, PressureSensor, HumiditySensor, Anemometer):

    def _watch(self, attr, new_value, old_value):
        super(OpenWeatherMapDevice, self)._watch(attr, new_value, old_value)

        if attr == 'weather':
            if new_value != old_value:
                self.dispatchSignal(SensorValueChanged(self, attr, new_value, old_value))

    @scheduler.setInterval(REFRESH_INTERVAL)
    def refresh(self):
        location = self.location
        if not location:
            self.log.error('no location set')
            return

        appid = self.core.get_plugin('OpenWeatherMap').config.get('appid')
        if appid:
            self.log.debug('fetch weather data')
            r = requests.get(url=API_WEATHER_URL, params=dict(q=location, APPID=appid, units='metric'))
            r.raise_for_status()
            data = r.json()
            if data:
                with self:
                    self.setConnectState(True)

                    self.log.debug('data read: %s' % (json.dumps(data)))

                    main = data.get('main', {})

                    if 'temp' in main:
                        self.temperature = main.get('temp')
                    if 'pressure' in main:
                        self.pressure = main.get('pressure') * 100
                    if 'humidity' in main:
                        self.humidity = main.get('humidity')

                    weather = data.get('weather', [])

                    if len(weather) > 0:
                        weather = weather[0]
                        if isinstance(weather, dict):
                            self.weather = weather.get('description', '')

                    if 'wind' in data:
                        wind = data.get('wind', {})

                        if 'speed' in wind:
                            self.wind_speed = wind.get('speed')
                            self.wind_direction = wind.get('deg', None)
        else:
            self.log.error('no appid set')
