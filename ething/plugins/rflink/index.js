(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;


    definitions.resources.RFLinkSerialGateway = {

        path: ['RFLink', 'Gateway'],

        label: 'RFLink Gateway (serial)',

        properties: {
            port: {
              format: 'serial'
            }
        }

    }

    definitions.resources.RFLinkNode = {

        disableCreation: true,

    }

    definitions.resources.RFLinkGenericSensor = {

        widgets: {
            'sensors': {
              label: 'sensor values',
              description: 'show all the sensors values',
              type: 'WGenericSensor'
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

    }


})(this);