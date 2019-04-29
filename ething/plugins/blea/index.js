(function(global){

    EThingUI.extend('resources/BleaGateway', {
        title: 'Bluetooth Gateway',
        icon: 'bluetooth',
    })

    EThingUI.extend('resources/BleaDevice', {
        disableCreation: true,
    })

    EThingUI.extend('resources/Miflora', {
        icon: 'mdi-flower',
        widgets: {
            'sensors': {
              in: 'dashboard',

              schema: {
                  title: 'sensor values',
                  description: 'show all the sensors values',
              },

              component: 'WGenericSensor'
            }
        }
    })

})(this);