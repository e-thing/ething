
import EThingUI from 'ething-ui'
import { iconPath, iconExt, weatherMap } from '../openweathermap'

const WDeviceMultiLabel = EThingUI.components.widgets.WDeviceMultiLabel


export default {
    name: 'WOpenWeatherMapDevice',

    extends: WDeviceMultiLabel,

    props: {

        items: {
            default () {
                return [{
                    label: 'temperature',
                    unit: '°C',
                    attr: 'temperature'
                },{
                    label: 'humidity',
                    unit: '%',
                    attr: 'humidity'
                },{
                    label: 'pressure',
                    unit: 'Pa',
                    attr: 'pressure'
                },{
                    label: 'weather',
                    attr: 'weather',
                    done () {
                        for (var i in weatherMap) {
                            if (this.value === weatherMap[i].description) {
                                if (weatherMap[i].icon) {
                                    var icon;
                                    if (Array.isArray(weatherMap[i].icon)) {
                                        var now = new Date()
                                        var hours = now.getHours()
                                        var index = hours >= 21 ? 1 : 0
                                        icon = weatherMap[i].icon[index]
                                    } else {
                                        icon = weatherMap[i].icon
                                    }
                                    this.icon = true
                                    this.value = iconPath + '/' + icon + '.' + iconExt
                                }
                                return
                            }
                        }
                    }
                }, {
                    label: 'wind speed',
                    attr: 'wind_speed',
                    unit: 'm/s',
                }, {
                    label: 'wind direction',
                    attr: 'wind_direction',
                    skipIfNull: true,
                    map: [{
                      key: 0,
                      value: 'N'
                    }, {
                      key: 45,
                      value: 'N-E'
                    }, {
                      key: 90,
                      value: 'E'
                    }, {
                      key: 135,
                      value: 'S-E'
                    }, {
                      key: 180,
                      value: 'S'
                    }, {
                      key: 225,
                      value: 'S-O'
                    }, {
                      key: 270,
                      value: 'O'
                    }, {
                      key: 315,
                      value: 'N-O'
                    }, {
                      key: 360,
                      value: 'N'
                    }]
                }]
            }
        }
    }
}

