(function(global){

    EThingUI.extend('resources/MihomeGateway', {
        disableCreation: true
    })

    EThingUI.extend('resources/MihomeDevice', {

        disableCreation: true,

        widgets: {
            'sensors': {
              schema: {
                  title: 'sensor values',
                  description: 'show all the sensors values',
              },
              component: 'WGenericSensor'
            }
        }

    })

})(this);