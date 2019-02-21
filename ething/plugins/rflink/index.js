(function(global){

    EThingUI.extend('resources/RFLinkSerialGateway', {

        category: 'RFLink.Gateway',

        title: 'RFLink Gateway (serial)'

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
        }

    })


})(this);