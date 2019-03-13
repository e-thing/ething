<template>
    <w-layout noFooter :title="city">
        <div class="overflow-hidden">
            <div class="row gutter-xs">
                <div v-for="item in items" class="col text-center">
                    <div class="date text-faded" v-if="mode!=='now'">
                        <small>
                            <template v-if="mode==='5d'">
                                {{ item.weekday }}
                            </template>
                            <template v-else>
                                {{ item.date.getHours() }}h
                            </template>
                        </small>
                    </div>
                    <img :src="item.iconUrl"/>
                    <div>
                        <span class="temperature text-faded">{{ rounded(mode==='5d' ? item.maxTemperature : item.temperature) }}°C</span>
                        <span class="humidity text-blue q-ml-xs">{{ rounded(item.humidity) }}%</span>
                    </div>
                    <div class="pressure text-faded" v-if="item.pressure">{{ rounded(item.pressure) }} Pa</div>
                    <div class="wind text-faded" v-if="item.windSpeed"><template v-if="item.windDirection">{{ item.windDirection }}</template> {{ rounded(item.windSpeed) }} m/s</div>
                </div>
            </div>
        </div>
    </w-layout>
</template>

<script>

import EThingUI from 'ething-ui'
import { getWeather, getWeatherForecast, iconPath, iconExt } from '../openweathermap'


const weekdays = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday'
]

// clear sky -> worst
const weatherConditionWeightMap = [
    [800, 899], // Clear + Clouds
    [700, 799], // Atmosphere
    [300, 399], // Drizzle
    [500, 599], // Rain
    [200, 299], // Thunderstorm
    [600, 699], // Snow
]

function weightedWeatherCondition (weatherConditionId) {
    for(var i in weatherConditionWeightMap) {

        var minIndex = weatherConditionWeightMap[i][0];
        var maxIndex = weatherConditionWeightMap[i][1];

        if (weatherConditionId >= minIndex && weatherConditionId <= maxIndex) {
            return i * 100 + (weatherConditionId - minIndex)
        }

    }
    return 0
}

function windDirection (deg) {

    if (typeof deg !== 'number') return ''

    const windDirectionMap = ['N', 'N-E', 'E', 'S-E', 'S', 'S-O', 'O', 'N-O', 'N']
    const windDirectionMapStep = 45

    var selectedIndex = null
    var diff = 0

    for (var i in windDirectionMap) {
        var ideg = i * windDirectionMapStep
        var d = deg - ideg
        if (selectedIndex===null || d < diff) {
            selectedIndex = i
            diff = d
        }
    }

    return selectedIndex !== null ? windDirectionMap[selectedIndex] : ''
}


export default {
    name: 'WOpenWeatherMapForecast',

    extends: EThingUI.components.widgets.WWidget,

    components: {
        WLayout: EThingUI.components.widgets.WLayout
    },

    props: {
        location: String,
        mode: {
            type: String,
            default: 'now'
        }
    },

    data () {
        var appid = null

        if (EThingUI.settings && EThingUI.settings.OpenWeatherMap) {
            appid = EThingUI.settings.OpenWeatherMap.appid
        }

        return {
            appid,
            raw: {},
            timerId: null
        }
    },

    computed: {

        city () {
            if (this.raw.city) return this.raw.city.name
            if (this.raw.name) return this.raw.name
        },

        twentyFourHoursItems () {
            var items = []
            if (this.raw.list && this.raw.cnt) {
                var now = Date.now()
                var end = now + 24 * 3600 * 1000
                this.raw.list.forEach(it => {
                    var dt = it.dt * 1000
                    if (dt <= end) {
                        items.push({
                            date: new Date(dt),
                            temperature: it.main.temp,
                            pressure: it.main.pressure,
                            humidity: it.main.humidity,
                            weather: it.weather.description,
                            icon: it.weather[0].icon,
                            iconUrl: iconPath + '/' + it.weather[0].icon + '.' + iconExt,
                            windSpeed: it.wind.speed,
                            windDirection: windDirection(it.wind.deg)
                        })
                    }
                })
            }
            return items
        },

        fiveDaysItems () {
            var items = []
            if (this.raw.list && this.raw.cnt) {
                var midnight = new Date();
                midnight.setHours(24,0,0,0);
                midnight = midnight.getTime();

                var item;
                function initItem() {
                    item = {
                        cnt: 0,
                        date: [],
                        temperature: [],
                        humidity: [],
                        weatherConditionWeight: [],
                        icon: [],
                    }
                }
                function endItem() {
                    var sum = (accumulator, currentValue) => accumulator + currentValue
                    var min = (accumulator, currentValue) => (accumulator < currentValue ? accumulator : currentValue)
                    var max = (accumulator, currentValue) => (accumulator > currentValue ? accumulator : currentValue)
                    if (item.cnt >= 1) {

                        item.minTemperature = item.temperature.reduce(min)
                        item.maxTemperature = item.temperature.reduce(max)
                        item.temperature = item.temperature.reduce(sum) / item.cnt
                        item.humidity = item.humidity.reduce(sum) / item.cnt

                        // select only hour beetween 9h and 18h(excluded)
                        var startd = new Date(item.date[0])
                        startd.setHours(9,0,0,0)
                        startd = startd.getTime()
                        var endd = new Date(item.date[0])
                        endd.setHours(17,0,0,0)
                        endd = endd.getTime()

                        var selectedIcon = null
                        var selectedW = null
                        for (var i in item.date) {
                            var dt = item.date[i]
                            if (dt >= startd && dt < endd) {
                                var w = item.weatherConditionWeight[i]
                                if (selectedW===null || selectedW > w) {
                                    selectedW = w
                                    selectedIcon = item.icon[i]
                                }
                            }
                        }

                        if (selectedW===null) {
                            for (var i in item.date) {
                                var w = item.weatherConditionWeight[i]
                                if (selectedW===null || selectedW > w) {
                                    selectedW = w
                                    selectedIcon = item.icon[i]
                                }
                            }
                        }

                        item.date = new Date(item.date[0])
                        item.weekday = weekdays[item.date.getDay()]

                        if (selectedW!==null && items.length < 5) {
                            item.icon = selectedIcon
                            item.weatherConditionWeight = selectedW
                            item.iconUrl = iconPath + '/' + item.icon + '.' + iconExt
                            items.push(item)
                        }
                    }
                }
                initItem()

                this.raw.list.forEach(it => {
                    var dt = it.dt * 1000

                    if (dt > midnight) {
                        midnight += 24 * 3600 * 1000
                        endItem()
                        // new day
                        initItem()
                    }

                    item.cnt += 1
                    item.date.push(dt)
                    item.temperature.push(it.main.temp)
                    item.humidity.push(it.main.humidity)
                    item.weatherConditionWeight.push(weightedWeatherCondition(it.weather[0].id))
                    item.icon.push(it.weather[0].icon)

                })

                endItem()
            }
            return items
        },

        nowItems () {
            var items = []
            if (this.raw.main) {
                items.push(
                    {
                        date: new Date(this.raw.dt * 1000),
                        temperature: this.raw.main.temp,
                        pressure: this.raw.main.pressure,
                        humidity: this.raw.main.humidity,
                        weather: this.raw.weather.description,
                        icon: this.raw.weather[0].icon,
                        iconUrl: iconPath + '/' + this.raw.weather[0].icon + '.' + iconExt,
                        windSpeed: this.raw.wind.speed,
                        windDirection: windDirection(this.raw.wind.deg)
                    }
                )
            }
            return items
        },

        items () {
            if (this.mode === '24h') {
                return this.twentyFourHoursItems
            }
            if (this.mode === '5d') {
                return this.fiveDaysItems
            }
            if (this.mode === 'now') {
                return this.nowItems
            }
            return []
        }

    },

    methods: {

        load () {
            var fncall = this.mode === 'now' ? getWeather : getWeatherForecast

            fncall(this.appid, this.location, data => {
                this.raw = data
            })
        },

        rounded (value, digits = 0) {
            return parseFloat(value).toFixed(digits);
        }

    },

    mounted () {
        if (this.appid) {
            this.load()
            this.timerId = setInterval(() => {
              this.load()
            }, 300000)
        } else {
            this.setError('no appid set in the plugin settings')
        }
    },

    beforeDestroy () {
      if(this.timerId !== null) {
        clearInterval(this.timerId)
      }
    }
}

</script>