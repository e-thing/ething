import WOpenWeatherMapDevice from './components/WOpenWeatherMapDevice'
import WOpenWeatherMapForecast from './components/WOpenWeatherMapForecast'
import EThingUI from 'ething-ui'


console.log('loading plugin OpenWeatherMap...')

// register globally this widget
EThingUI.registerWidget('OpenWeatherMapForecast', {
    component: WOpenWeatherMapForecast,
    schema: {
        title: 'OpenWeatherMap forecast widget',
        description: 'display weather forecast',
        properties: {
            location: {
                type: 'string',
                minLength: 1
            },
            mode: {
                enum: ['now', '24h', '5d']
            }
        }
    },
    minHeight: 120
})


EThingUI.extend('resources/OpenWeatherMapDevice', {

    icon: 'mdi-weather-partlycloudy',

    widgets: {

        'default': {
            in: ['devicePage', 'dashboard'],
            component: WOpenWeatherMapDevice,
            schema: {
                title: 'default widget',
                description: 'display the current weather informations',
            },
            minHeight: 250,
            zIndex: 100
        }

    }

})










