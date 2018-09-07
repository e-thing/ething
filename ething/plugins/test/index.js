(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;
    var widget = global.widget
    var WDeviceLabel = widget.find('WDeviceLabel')


    /*
    * Customize some properties on the client side
    */
    definitions.resources.RandomThermometer = {

        disableCreation: true,

        widgets: {

            'custom': {
                label: 'custom widget',
                description: 'show the temperature',
                type: 'WCustomThermometer'
            }

        }

    }

    widget.register({
        name: 'WCustomThermometer',

        template: '<WDeviceLabel attr="temperature" unit="°C" @error="$emit(\'error\', $event)"/>',

        components: [WDeviceLabel]

    })


})(this);
