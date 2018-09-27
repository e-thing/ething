import WOpenWeatherMapDevice from './components/WOpenWeatherMapDevice'
import EThingUI from 'ething-quasar-core'

console.log('loading plugin OpenWeatherMap...')

EThingUI.registerWidget(WOpenWeatherMapDevice)

EThingUI.extend('resources/OpenWeatherMapDevice', {

    icon: 'mdi-weather-partlycloudy',

    widgets: {

        'default': 'WOpenWeatherMapDevice'

    }

})









