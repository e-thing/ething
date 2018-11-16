
import MainComponent from './components/Main'
import EThingUI from 'ething-quasar-core'
require('./shell.js')

EThingUI.extend('resources/SSH', {
    icon: 'mdi-console',

    mainComponent: MainComponent,

    properties: {
        host: {
          format: 'host'
        }
    }

})
