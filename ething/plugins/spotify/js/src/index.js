
import MainComponent from './components/Main'
import SpotifyWidget from './components/SpotifyWidget'
import EThingUI from 'ething-ui'



EThingUI.extend('resources/SpotifyAccount', {

    icon: 'mdi-spotify',

    components (resource) {
      return {
        'spotify': {
          component: 'widget',
          title: 'Spotify',
          description: 'play music on your device',
          attributes () {
            return {
              widget: 'spotify',
              height: '300px'
            }
          }
        },
        'main': {
          title: 'Account',
          component: MainComponent
        }
      }
    },

    widgets (resource) {
      return {
        'spotify': {
          component: SpotifyWidget,
          title: 'Spotify',
          description: 'play music on your device',
          minHeight: 250,
          minWidth: 500
        }
      }
    }

})
