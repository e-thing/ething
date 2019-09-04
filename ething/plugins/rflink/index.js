(function(global){

    EThingUI.extend('resources/RFLinkGateway', {

        category: 'RFLink',

        title: 'RFLink Gateway (serial)'

    })

    EThingUI.extend('resources/RFLinkGenericSensor', {

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