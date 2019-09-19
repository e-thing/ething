
import MainComponent from './components/Main'
import EThingUI from 'ething-ui'
require('./shell.js')

EThingUI.extend('resources/SSH', {
    icon: 'mdi-console',

    components (resource) {
      return {
        'main': {
            component: MainComponent,
            title: 'Command prompt',
            icon: 'mdi-console',
        }
      }
    },

})
