import EThingUI from 'ething-quasar-core'
import WScript from './components/WScript'
import ScriptPage from './pages/Script'


// register script specific widget
EThingUI.registerWidget(WScript)


// extend File type

var nativeFileOpenFn = EThingUI.definitions.resources.File.open

EThingUI.extend('resources/File', {

    open (resource, more) {

        if ('application/javascript' == resource.mime()) {
            return '/script/' + resource.id()
        }

        return nativeFileOpenFn.call(this, resource, more)
    },

    dynamic (resource) {

        if (resource.mime() === 'application/javascript') {
          return {
              widgets: {
                script: 'WScript'
              }
          }
        }

    }

})

// extend RunScript action
EThingUI.extend('actions/RunScript', {

    properties: {
        script: {
          format: 'ething.resource',
          filter: (r) => {
            return (r instanceof EThing.File) && r.mime() == 'application/javascript'
          }
        },
    }

})



// add a new route
var router = EThingUI.router
var main = router.options.routes[0]

main.children = [{
    path: 'script/:id',
    component: ScriptPage,
    meta: {
      back: true
    }
}]

router.addRoutes([main])







