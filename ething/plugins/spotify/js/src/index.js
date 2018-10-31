
import MainComponent from './components/Main'
import SpotifyWidget from './components/SpotifyWidget'
import EThingUI from 'ething-quasar-core'



EThingUI.extend('resources/SpotifyAccount', {

    icon: 'mdi-spotify',

    mainComponent: MainComponent,

    widgets: {
      'spotify': SpotifyWidget
    }

})
