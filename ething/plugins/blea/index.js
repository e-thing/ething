(function(global){

    EThingUI.extend('resources/BleaGateway', {

        title: 'Bluetooth Gateway',

        icon: 'bluetooth',

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