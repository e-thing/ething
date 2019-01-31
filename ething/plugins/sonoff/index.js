(function(global){

    EThingUI.extend('resources/Sonoff_http', {

        title: 'Sonoff (http)',

        properties: {
            secure: {
                _disabled: true
            },
            host: {
              format: 'host'
            }
        }

    })


})(this);