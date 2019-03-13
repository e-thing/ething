
import MainComponent from './components/Main'
import SpotifyWidget from './components/SpotifyWidget'
import EThingUI from 'ething-ui'



EThingUI.extend('resources/SpotifyAccount', {

    icon: 'mdi-spotify',

    widgets: {
      'spotify': {
        in: ['devicePage', 'dashboard'],
        component: SpotifyWidget,
        schema: {
            title: 'Spotify widget',
            description: 'play music on your device',
        },
        minHeight: 250,
        minWidth: 500
      },
      'main': {
        in: 'devicePage',
        component: MainComponent
      }
    }

})
