(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;


    definitions.resources.ZigateSerialGateway = {

        path: ['Zigate', 'Gateway'],

        label: 'Zigate Gateway (serial)',

        properties: {
            port: {
              format: 'serial'
            }
        }

    }


})(this);