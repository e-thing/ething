
import SpotifyWidget from './components/SpotifyWidget'
import EThingUI from 'ething-ui'


EThingUI.extend('resources/SpotifyAccount', {

    components (resource) {
      return {
        'spotify': {
          component: 'widget',
          title: 'Spotify',
          attributes () {
            return {
              widget: 'spotify',
              height: '400px'
            }
          }
        },
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
