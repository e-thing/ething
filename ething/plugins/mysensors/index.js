(function(global){

    const types = {
      'S_DOOR': { icon: 'mdi-door' },
      'S_MOTION': { icon: 'mdi-transition' },
      'S_SMOKE': { icon: 'mdi-smoke-detector' },
      'S_LIGHT': {},
      'S_BINARY': {},
      'S_DIMMER': {},
      'S_COVER': {},
      'S_TEMP': {},
      'S_HUM': { icon: 'mdi-water-percent', widgets: [{type: 'WDeviceKnob', options: { fn: 'getHumidity', unit: '%'}}, {type: 'WDeviceLabel', options: { fn: 'getHumidity', unit: '%'}}] },
      'S_BARO': { widgets: [{type: 'WDeviceLabel', options: { fn: 'getPressure', unit: 'Pa'}}] },
      'S_WIND': { icon: 'mdi-weather-windy' },
      'S_RAIN': { icon: 'mdi-weather-rainy' },
      'S_UV': { icon: 'mdi-weather-sunny' },
      'S_WEIGHT': { icon: 'mdi-weight' },
      'S_POWER': { icon: 'mdi-power-plug' },
      'S_HEATER': { icon: 'mdi-fire' },
      'S_DISTANCE': { icon: 'mdi-map-marker-distance' },
      'S_LIGHT_LEVEL': { icon: 'mdi-lightbulb-on-outline' },
      'S_ARDUINO_NODE': { icon: 'mdi-chip' },
      'S_ARDUINO_REPEATER_NODE': { icon: 'mdi-repeat' },
      'S_LOCK': { icon: 'mdi-lock' },
      'S_IR': {},
      'S_WATER': { icon: 'mdi-water', widgets: [{type: 'WDeviceLabel', options: { fn: 'getVolume', unit: 'L'}}] },
      'S_AIR_QUALITY': {},
      'S_CUSTOM': {},
      'S_DUST': {},
      'S_SCENE_CONTROLLER': {},
      'S_RGB_LIGHT': {},
      'S_RGBW_LIGHT': {},
      'S_COLOR_SENSOR': { icon: 'mdi-palette' },
      'S_HVAC': { icon: 'mdi-air-conditioner' },
      'S_MULTIMETER': { icon: 'mdi-power-plug' },
      'S_SPRINKLER': { icon: 'mdi-water-pump' },
      'S_WATER_LEAK': { icon: 'mdi-pipe-leak' },
      'S_SOUND': { icon: 'mdi-surround-sound' },
      'S_VIBRATION': { icon: 'mdi-vibrate' },
      'S_MOISTURE': { icon: 'mdi-water-percent' },
      'S_INFO': { icon: 'mdi-information' },
      'S_GAS': { icon: 'mdi-gas-cylinder' },
      'S_GPS': { icon: 'mdi-crosshairs-gps' },
      'S_WATER_QUALITY': { icon: 'mdi-water' },
      'S_CAM': { icon: 'mdi-camera' },
      'S_UNK': { icon: 'mdi-help' },
    }


    EThingUI.extend('resources/MySensorsEthernetGateway', {

        path: ['MySensors', 'Gateway'],

        label: 'MySensors Gateway (ethernet)',

        properties: {
            host: {
              format: 'host'
            }
        }

    })

    EThingUI.extend('resources/MySensorsSerialGateway', {

        path: ['MySensors', 'Gateway'],

        label: 'MySensors Gateway (serial)',

        properties: {
            port: {
              format: 'serial'
            }
        }

    })

    EThingUI.extend('resources/MySensorsNode', {

        disableCreation: true,

    })

    EThingUI.extend('resources/MySensorsSensor', {

        disableCreation: true,

        properties: {
            sensorType: {
              enum: Object.keys(types)
            },
        },

        dynamic (resource) {
            var sensorType = resource.attr('sensorType')
            return types[sensorType]
        }

    })

    EThingUI.extend('resources/MySensorsGenericSensor', {

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