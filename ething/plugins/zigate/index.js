(function(global){

    EThingUI.extend('resources/ZigateSerialGateway', {

        path: ['Zigate', 'Gateway'],

        label: 'Zigate Gateway (serial)',

        properties: {
            port: {
              '$component': 'serial'
            }
        }

    })


})(this);