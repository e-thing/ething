import WOpenWeatherMapDevice from './components/WOpenWeatherMapDevice'
import WOpenWeatherMapForecast from './components/WOpenWeatherMapForecast'
import EThingUI from 'ething-ui'
import "./statics/css/weather-icons.css"


// register globally this widget
EThingUI.registerWidget('OpenWeatherMapForecast', {
    component: WOpenWeatherMapForecast,
    title: 'OpenWeatherMap forecast widget',
    description: 'display weather forecast',
    schema: {
        properties: {
            location: {
                type: 'string',
                minLength: 1
            },
        },
        required: ['location']
    },
    minHeight: 120
})

EThingUI.extend('resources/OpenWeatherMapDevice', {

    icon: 'mdi-weather-partlycloudy',

    components (resource) {
      return {
        'default': {
            component: 'widget',
            title: 'weather informations',
            attributes () {
              return {
                widget: 'default',
                height: '250px'
              }
            }
        }
      }
    },

    widgets (resource) {
      return {
        'default': {
            component: WOpenWeatherMapDevice,
            title: 'weather informations',
            description: 'display the current weather informations',
            minHeight: 250,
            zIndex: 100
        }
      }
    }

})
