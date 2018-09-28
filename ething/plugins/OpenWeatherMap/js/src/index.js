import WOpenWeatherMapDevice from './components/WOpenWeatherMapDevice'
import WOpenWeatherMapForecast from './components/WOpenWeatherMapForecast'
import EThingUI from 'ething-quasar-core'


console.log('loading plugin OpenWeatherMap...')

EThingUI.registerWidget(WOpenWeatherMapDevice)
EThingUI.registerWidget(WOpenWeatherMapForecast)

EThingUI.extend('resources/OpenWeatherMapDevice', {

    icon: 'mdi-weather-partlycloudy',

    widgets: {

        'default': 'WOpenWeatherMapDevice'

    }

})










