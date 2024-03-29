# coding: utf-8

from ething.plugin import *
from ething.scheduler import set_interval
from ething.Device import *
from ething.interfaces import Thermometer, PressureSensor, HumiditySensor, Anemometer
from ething.interfaces.sensor import sensor_attr
import requests
import json
import logging


LOGGER = logging.getLogger(__name__)


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
            LOGGER.warning('no appid set in the configuration')
            self.notification.warning('no appid set in the configuration', title='Open Weather Map', id='owm.appid.check')
        else:
            self.notification.remove('owm.appid.check')

    def on_config_change(self, dirty_attributes):
        if not self.appid:
            LOGGER.warning('no appid set in the configuration')
            self.notification.warning('no appid set in the configuration', title='Open Weather Map', id='owm.appid.check')
        else:
            # refresh all devices
            self.notification.remove('owm.appid.check')
            LOGGER.debug('appid changed in the configuration')
            for d in self.core.find(OpenWeatherMapDevice):
                d.refresh()



@sensor_attr('weather', type=String(), default='', description='a string descibing the current weather')
@attr('location', type=String(allow_empty=False), default=NO_VALUE, description='a city\'s name. See https://openweathermap.org/find')
class OpenWeatherMapDevice(Thermometer, PressureSensor, HumiditySensor, Anemometer):

    def on_attr_update(self, attr, new_value, old_value):
        super(OpenWeatherMapDevice, self).on_attr_update(attr, new_value, old_value)
        if attr == 'location':
            self.processes.add(self.refresh)

    @set_interval(REFRESH_INTERVAL)
    def refresh(self):
        location = self.location
        if not location:
            self.error = 'no location set'
            return

        appid = self.core.plugins['OpenWeatherMap'].appid
        if appid:
            self.error = None
            self.logger.debug('fetch weather data')
            r = requests.get(url=API_WEATHER_URL, params=dict(q=location, APPID=appid, units='metric'))

            if r.status_code == requests.codes.ok:

                data = r.json()

                if data:
                    with self:
                        self.refresh_connect_state(True)

                        self.logger.debug('data read: %s', json.dumps(data))

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
                # invalid request
                self.refresh_connect_state(False)
                try:
                    data = r.json()
                    # get some error code
                    if 'message' in data:
                        self.error = data.get('message')
                except:
                    pass

                r.raise_for_status()
        else:
            self.error = 'no appid set'
            self.refresh_connect_state(False)
