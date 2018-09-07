(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;


    definitions.resources.BleaGateway = {

        label: 'Bluetooth Gateway',

        icon: 'bluetooth',

        properties: {
            iface: {
              title: 'interface',
              format: 'bluetooth-interface'
            }
        }

    }

    definitions.resources.Miflora = {

        icon: 'mdi-flower',

        widgets: {
            'sensors': {
              label: 'sensor values',
              description: 'show all the sensors values',
              type: 'WGenericSensor'
            }
        }

    }



})(this);