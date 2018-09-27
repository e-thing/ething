
import EThingUI from 'ething-quasar-core'

const WDeviceMultiLabel = EThingUI.widgets.WDeviceMultiLabel

const iconPath = 'http://openweathermap.org/img/w'
const iconExt = 'png'
const weatherMap = [
    {id: '200', description: 'thunderstorm with light rain', icon: '11d'},
    {id: '201', description: 'thunderstorm with rain', icon: '11d'},
    {id: '202', description: 'thunderstorm with heavy rain', icon: '11d'},
    {id: '210', description: 'light thunderstorm', icon: '11d'},
    {id: '211', description: 'thunderstorm', icon: '11d'},
    {id: '212', description: 'heavy thunderstorm', icon: '11d'},
    {id: '221', description: 'ragged thunderstorm', icon: '11d'},
    {id: '230', description: 'thunderstorm with light drizzle', icon: '11d'},
    {id: '231', description: 'thunderstorm with drizzle', icon: '11d'},
    {id: '232', description: 'thunderstorm with heavy drizzle', icon: '11d'},
    {id: '300', description: 'light intensity drizzle', icon: '09d'},
    {id: '301', description: 'drizzle', icon: '09d'},
    {id: '302', description: 'heavy intensity drizzle', icon: '09d'},
    {id: '310', description: 'light intensity drizzle rain', icon: '09d'},
    {id: '311', description: 'drizzle rain', icon: '09d'},
    {id: '312', description: 'heavy intensity drizzle rain', icon: '09d'},
    {id: '313', description: 'shower rain and drizzle', icon: '09d'},
    {id: '314', description: 'heavy shower rain and drizzle', icon: '09d'},
    {id: '321', description: 'shower drizzle', icon: '09d'},
    {id: '500', description: 'light rain', icon: '10d'},
    {id: '501', description: 'moderate rain', icon: '10d'},
    {id: '502', description: 'heavy intensity rain', icon: '10d'},
    {id: '503', description: 'very heavy rain', icon: '10d'},
    {id: '504', description: 'extreme rain', icon: '10d'},
    {id: '511', description: 'freezing rain', icon: '13d'},
    {id: '520', description: 'light intensity shower rain', icon: '09d'},
    {id: '521', description: 'shower rain', icon: '09d'},
    {id: '522', description: 'heavy intensity shower rain', icon: '09d'},
    {id: '531', description: 'ragged shower rain', icon: '09d'},
    {id: '600', description: 'light snow', icon: '13d'},
    {id: '601', description: 'snow', icon: '13d'},
    {id: '602', description: 'heavy snow', icon: '13d'},
    {id: '611', description: 'sleet', icon: '13d'},
    {id: '612', description: 'shower sleet', icon: '13d'},
    {id: '615', description: 'light rain and snow', icon: '13d'},
    {id: '616', description: 'rain and snow', icon: '13d'},
    {id: '620', description: 'light shower snow', icon: '13d'},
    {id: '621', description: 'shower snow', icon: '13d'},
    {id: '622', description: 'heavy shower snow', icon: '13d'},
    {id: '701', description: 'mist', icon: '50d'},
    {id: '711', description: 'smoke', icon: '50d'},
    {id: '721', description: 'haze', icon: '50d'},
    {id: '731', description: 'sand, dust whirls', icon: '50d'},
    {id: '741', description: 'fog', icon: '50d'},
    {id: '751', description: 'sand', icon: '50d'},
    {id: '761', description: 'dust', icon: '50d'},
    {id: '762', description: 'volcanic ash', icon: '50d'},
    {id: '771', description: 'squalls', icon: '50d'},
    {id: '781', description: 'tornado', icon: '50d'},
    {id: '800', description: 'clear sky', icon: ['01d', '01n']},
    {id: '801', description: 'few clouds', icon: ['02d', '02n']},
    {id: '802', description: 'scattered clouds', icon: ['03d', '03n']},
    {id: '803', description: 'broken clouds', icon: ['04d', '04n']},
    {id: '804', description: 'overcast clouds', icon: ['04d', '04n']},
]

export default {
    name: 'WOpenWeatherMapDevice',

    extends: WDeviceMultiLabel,

    metadata: {
        label: 'default widget',
        description: 'display the current weather informations',
        minHeight: 250
    },

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
                    }]
                }]
            }
        }
    }
}

