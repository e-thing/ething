(function(global){

    EThingUI.extend('resources/RFLinkSerialGateway', {

        path: ['RFLink', 'Gateway'],

        label: 'RFLink Gateway (serial)',

        properties: {
            port: {
              '$component': 'serial'
            }
        }

    })

    EThingUI.extend('resources/RFLinkNode', {

        disableCreation: true,

    })

    EThingUI.extend('resources/RFLinkGenericSensor', {

        widgets: {
            'sensors': {
              metadata: {
                  label: 'sensor values',
                  description: 'show all the sensors values',
              },
              extends: EThingUI.widgets.WGenericSensor
            }
        },

        dynamic (resource) {

            var interfaces = resource.types().filter(t => /^interfaces\//.test(t))

            // copy
            var m = {}

            interfaces.forEach(interfaceName => {
              // extend
              meta.mergeClass(m, meta.get(interfaceName, true))
            })

            return m
        }

    })


})(this);