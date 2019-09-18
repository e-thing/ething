import EThingUI from 'ething-ui'
import GoogleAccounts from './components/GoogleAccounts'
import GoogleUserForm from './components/GoogleUserForm'
import WGoogleCalendar from './components/WGoogleCalendar'


EThingUI.extend('plugins/google', {

    components (plugin) {
      return {
        'accounts': {
            component: GoogleAccounts,
            title: 'accounts',
        }
      }
    },

})

EThingUI.form.registerForm(GoogleUserForm)

EThingUI.extend('resources/GoogleCalendar', {

    components (resource) {
      return {
        'default': {
            component: 'widget',
            icon: 'mdi-calendar',
            title: 'Calendar',
            attributes () {
              return {
                widget: 'main',
                height: '400px'
              }
            }
        }
      }
    },

    widgets (resource) {
      return {
        'default': {
            component: WGoogleCalendar,
            title: 'Calendar',
            description: 'display the events',
            minHeight: 250,
            zIndex: 100
        }
      }
    },

})
