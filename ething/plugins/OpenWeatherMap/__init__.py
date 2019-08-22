# coding: utf-8

from ething.plugin import *
from ething import scheduler
from ething.Device import *
from ething.interfaces import Thermometer, PressureSensor, HumiditySensor, Anemometer
from ething.interfaces.sensor import sensor_attr
import requests
import json


API_WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'

REFRESH_INTERVAL = 300 # in seconds


@attr('appid', type=String(), default='', description='Your API ID from OpenWeatherMap. See https://openweathermap.org/appid .')
class OpenWeatherMapPlugin(Plugin):

    """
    OpenWeatherMap plugin. Allow you to get the weather for any city.
    """

    JS_INDEX = './js/index.js'

    def setup(self):
        if not self.appid:
            self.log.warning('no appid set in the configuration')

    def on_config_change(self, dirty_attributes):
        if not self.appid:
            self.log.warning('no appid set in the configuration')
        else:
            # refresh all devices
            self.log.debug('appid changed in the configuration')
            for d in self.core.find(OpenWeatherMapDevice):
                d.refresh()



@sensor_attr('weather', type=String(), default='', description='a string descibing the current weather')
@attr('location', type=String(allow_empty=False), default=NO_VALUE, description='a city\'s name. See https://openweathermap.org/find')
class OpenWeatherMapDevice(Thermometer, PressureSensor, HumiditySensor, Anemometer):

    @scheduler.set_interval(REFRESH_INTERVAL)
    def refresh(self):
        location = self.location
        if not location:
            self.error = 'no location set'
            return

        appid = self.core.get_plugin('OpenWeatherMap').appid
        if appid:
            self.error = None
            self.log.debug('fetch weather data')
            r = requests.get(url=API_WEATHER_URL, params=dict(q=location, APPID=appid, units='metric'))
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                self.refresh_connect_state(False)
                raise e
            else:
                data = r.json()
                if data:
                    with self:
                        self.refresh_connect_state(True)

                        self.log.debug('data read: %s', json.dumps(data))

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
            self.error = 'no appid set'
            self.refresh_connect_state(False)
