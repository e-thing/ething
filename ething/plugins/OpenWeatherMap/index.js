(function(global){

    var meta = global.meta;
    var definitions = meta.definitions;
    var widget = global.widget
    var WDeviceLabel = widget.find('WDeviceLabel')


    /*
    * Customize some properties on the client side
    */
    definitions.resources.OpenWeatherMapDevice = {

        widgets: {

            'default': {
                label: 'default widget',
                description: 'display the current weather informations',
                type: 'WDeviceMultiLabel',
                options: {
                    items: [{
                        key: 'temperature',
                        unit: '°C',
                        attr: 'temperature'
                    },{
                        key: 'humidity',
                        unit: '%',
                        attr: 'humidity'
                    },{
                        key: 'pressure',
                        unit: 'Pa',
                        attr: 'pressure'
                    }]
                }
            }

        }

    }


})(this);
