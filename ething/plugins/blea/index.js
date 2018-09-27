(function(global){

    EThingUI.extend('resources/BleaGateway', {

        label: 'Bluetooth Gateway',

        icon: 'bluetooth',

        properties: {
            iface: {
              title: 'interface',
              format: 'bluetooth-interface'
            }
        }

    })

    EThingUI.extend('resources/Miflora', {

        icon: 'mdi-flower',

        widgets: {
            'sensors': {
              metadata: {
                  label: 'sensor values',
                  description: 'show all the sensors values',
              },
              extends: EThingUI.widgets.WGenericSensor
            }
        }

    })

})(this);