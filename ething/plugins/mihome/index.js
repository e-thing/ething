(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;


    definitions.resources.MihomeGateway = {

        disableCreation: true

    }

    definitions.resources.MihomeDevice = {

        disableCreation: true,

        widgets: {
            'sensors': {
              label: 'sensor values',
              description: 'show all the sensors values',
              type: 'WGenericSensor'
            }
        }

    }



})(this);