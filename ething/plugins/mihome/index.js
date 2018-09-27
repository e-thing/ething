(function(global){

    EThingUI.extend('resources/MihomeGateway', {
        disableCreation: true
    })

    EThingUI.extend('resources/MihomeDevice', {

        disableCreation: true,

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