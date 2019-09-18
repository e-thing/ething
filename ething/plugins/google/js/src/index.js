import EThingUI from 'ething-ui'
import WGoogleAccounts from './components/WGoogleAccounts'


EThingUI.extend('plugins/google', {

    components (plugin) {
      return {
        'accounts': {
            component: WGoogleAccounts,
            title: 'accounts',
        }
      }
    },

})
