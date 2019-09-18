<template>
  <div class="column q-px-md q-pt-md no-wrap fit">
    <template v-if="hasData">
      <div class="col-auto cityname text-bold">
        {{ city }}
      </div>
      <q-space/>
      <div class="col-grow now text-center">
        <div>
          <i class="icon q-mr-md" :class="current.weatherIcon"></i>
          <!--<q-icon class="icon" :name="current.weatherIcon"/>-->
          <span class="value">{{ current.temperature }}</span>
          <span class="unit">{{ temperatureUnit }}</span>
        </div>
        <div class="label">
          {{ current.weatherLabel }}
        </div>
      </div>
      <div class="col-shrink">
        <div class="today q-my-sm" v-if="today">
          <div class="text-bold">{{ today.day }}</div>
          <div class="row">
            <div class="col-4">
              <q-icon name="mdi-weather-sunset-up"/> {{ today.sunrise }}
            </div>
            <div class="col-3">
              Max {{ today.temperatureMax }}{{ temperatureUnit }}
            </div>
            <div class="col-5">
              <q-icon name="mdi-water"/> {{ today.humidity }} %
            </div>
          </div>
          <div class="row">
            <div class="col-4">
              <q-icon name="mdi-weather-sunset-down"/> {{ today.sunset }}
            </div>
            <div class="col-3">
              Min {{ today.temperatureMin }}{{ temperatureUnit }}
            </div>
            <div class="col-5">
              <q-icon name="mdi-scale"/> {{ today.pressure }} {{ pressureUnit }}
            </div>
          </div>
          <div class="row">
            <div class="col-5 offset-7">
              <q-icon name="mdi-weather-windy"/> {{ today.windDirection }} {{ today.windSpeed }} {{ windSpeedUnit }}
            </div>
          </div>
        </div>
        <template v-for="item in forecast" v-if="forecast && forecast.length>0">
          <q-separator/>
          <div class="forecast row q-my-sm items-center">
            <div class="col-4 text-bold">
              {{ item.day }}
            </div>
            <div class="col-3">
              <i class="icon" :class="item.weatherIcon"></i>
              <!--<q-icon class="icon" :name="item.weatherIcon" size="200%" />-->
            </div>
            <div class="col-3">
              {{ item.temperatureMax }}{{ temperatureUnit }}
            </div>
            <div class="col-2">
              {{ item.temperatureMin }}{{ temperatureUnit }}
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<script>

import EThingUI from 'ething-ui'
import { getWeather, getWeatherForecast, iconPath, iconExt, formatWindDirection, weightedWeatherCondition, toWeatherIcon  } from '../openweathermap'


const weekdays = [
    'Sunday', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday'
]


export default {
    name: 'WOpenWeatherMapForecast',

    extends: EThingUI.components.widgets.Base,

    props: {
        location: String,
    },

    data () {
        var appid = null

        if (EThingUI.settings && EThingUI.settings.OpenWeatherMap) {
            appid = EThingUI.settings.OpenWeatherMap.appid
        }

        return {
            appid,
            timerId: null,

            weatherData: null,
            forecastData: null,

            temperatureUnit: '°C',
            pressureUnit: 'hPa',
            windSpeedUnit: 'km/h'
        }
    },

    computed: {

        hasData () {
          return this.weatherData && this.forecastData
        },
        city () {
          return this.weatherData.name
        },
        current () {
          /*
          {
            temperature: 13,
            weatherIcon: 'mdi-weather-cloudy',
            weatherLabel: 'Partly Cloudy'
          }
          */
          var weather = this.weatherData.weather[0] || {}
          return {
            temperature: Math.round(this.weatherData.main.temp),
            humidity: Math.round(this.weatherData.main.humidity),
            pressure: Math.round(this.weatherData.main.pressure),
            weatherIcon: toWeatherIcon(weather.id, this.weatherData),  //'img:' + iconPath + '/' + weather.icon + '.' + iconExt,
            weatherLabel: weather.description
          }
        },

        today () {
          return {
            day: this.dailyData[0].weekday,
            sunrise: EThingUI.utils.formatDate(this.weatherData.sys.sunrise * 1000, 'HH:mm'),
            sunset: EThingUI.utils.formatDate(this.weatherData.sys.sunset * 1000, 'HH:mm'),
            temperatureMin: Math.round(this.dailyData[0].temperatureMin),
            temperatureMax: Math.round(this.dailyData[0].temperatureMax),
            humidity: Math.round(this.dailyData[0].humidityMax),
            pressure: Math.round(this.dailyData[0].pressure),
            windDirection: formatWindDirection(this.dailyData[0].windDirection),
            windSpeed: Math.round(this.dailyData[0].windSpeedMax),
          }
        },

        forecast () {
          var forecast = []
          this.dailyData.forEach((d,i) => {
            if (i==0) return
            if (d.len<6) return
            forecast.push({
              day: d.weekday,
              weatherIcon: toWeatherIcon(d.weather.id), // d.weather.icon ? ('img:' + iconPath + '/' + d.weather.icon + '.' + iconExt) : null,
              temperatureMin: Math.round(d.temperatureMin),
              temperatureMax: Math.round(d.temperatureMax),
            })
          })
          return forecast
        },

        dailyData () {
          var dailyData = []
          var tmpDataList = []
          var tmpDay = null
          this.forecastData.list.forEach(data => {
            var day = data.dt_txt.split(' ')[0]
            if (day !== tmpDay) {
              if (tmpDataList.length>0) dailyData.push(tmpDataList)
              tmpDataList = []
              tmpDay = day
            }
            tmpDataList.push(data)
          })

          if (tmpDataList.length>0) {
            dailyData.push(tmpDataList)
          }

          // compile
          return dailyData.map(dataList => {
            var temperatureMin = null,
              temperatureMax = null,
              humidityMax = null,
              pressure = 0,
              windSpeedMax = null,
              windDirection = 0, windDirectionCnt=0,
              weather = {}, weatherWeight = null;

            dataList.forEach(d => {
              if (temperatureMin===null || d.main.temp < temperatureMin) temperatureMin = d.main.temp
              if (temperatureMax===null || d.main.temp > temperatureMax) temperatureMax = d.main.temp
              if (humidityMax===null || d.main.humidity > humidityMax) humidityMax = d.main.humidity
              pressure += d.main.pressure
              if (d.wind && typeof d.wind.speed === 'number') {
                if (windSpeedMax===null || d.wind.speed > windSpeedMax) windSpeedMax = d.wind.speed
              }
              if (d.wind && typeof d.wind.deg === 'number') {
                windDirection += d.wind.deg
                windDirectionCnt += 1
              }
              if (d.weather && d.weather.length > 0) {
                var w = weightedWeatherCondition(d.weather[0].id)
                if (weatherWeight===null || w > weatherWeight) {
                  weatherWeight = w
                  weather = d.weather[0]
                }
              }
            })

            pressure /= dataList.length

            windDirection = windDirectionCnt>0 ? windDirection/windDirectionCnt : null

            var date = new Date(dataList[0].dt * 1000)
            var weekday = weekdays[date.getDay()]

            return {
              temperatureMin,
              temperatureMax,
              humidityMax,
              pressure,
              windSpeedMax,
              windDirection,
              weather,
              weekday,
              len: dataList.length
            }
          })

        },

    },

    methods: {

        load () {
            getWeather(this.appid, this.location, data => {
              //console.log('getWeather', data)
              this.weatherData = data
            })
            getWeatherForecast(this.appid, this.location, data => {
              //console.log('getWeatherForecast', data)
              this.forecastData = data
            })
        },

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

<style lang="stylus" scoped>

.light
  filter: brightness(110%)

.cityname
  font-size: 150%

.now .value
  font-size: 400%

.now .icon
  font-size: 400%

.now .label
  font-size: 150%

.today > .row
  font-size: 80%

</style>
