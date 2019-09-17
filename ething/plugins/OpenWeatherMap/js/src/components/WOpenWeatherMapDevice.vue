<template>
  <div class="fit items-center no-wrap" :class="wide ? 'row justify-around' : 'column justify-center q-gutter-y-md'">
    <q-resize-observer @resize="onResize" />
    <div class="col-auto text-center main" :style="small ? '' : 'font-size: 200%;'">
      <div class="row items-center" style="font-size: 200%;line-height: 1em;">
        <!--<q-icon class="col-auto icon" :name="weatherIcon"/>-->
        <i class="col-auto icon q-mr-sm" :class="weatherIcon"></i>
        <div class="col">
            <span class="value">{{ temperature }}</span>
            <span class="unit" style="font-size: 50%; line-height: 1em;">{{ temperatureUnit }}</span>
        </div>
      </div>
      <div style="font-size: 100%;">{{ weatherLabel }}</div>
    </div>
    <div class="col-auto" :style="small ? 'font-size: 80%;' : ''" v-show="details">
      <div>
        <div><q-icon class="q-mr-xs" name="mdi-weather-windy"/> <span v-show="labels">wind:</span> {{ windDirection }} {{ windSpeed }}{{ windSpeedUnit }}</div>
        <div><q-icon class="q-mr-xs" name="mdi-water"/> <span v-show="labels">humidity:</span> {{ humidity }}%</div>
        <div><q-icon class="q-mr-xs" name="mdi-scale"/> <span v-show="labels">pressure:</span> {{ pressure }}{{ pressureUnit }}</div>
      </div>
    </div>
  </div>
</template>

<script>

import EThingUI from 'ething-ui'
import { iconPath, iconExt, weatherMap, formatWindDirection, toWeatherIcon } from '../openweathermap'


export default {
    name: 'WOpenWeatherMapDevice',

    extends: EThingUI.components.widgets.Base,

    data () {
      return {
        temperatureUnit: '°C',
        pressureUnit: 'mbar',
        windSpeedUnit: 'km/h',
        small: false,
        wide: false,
        labels: true,
        details: true
      }
    },

    computed: {
      temperature () {
        return Math.round(this.resource.attr('temperature'))
      },
      humidity () {
        return Math.round(this.resource.attr('humidity'))
      },
      pressure () {
        return Math.round(this.resource.attr('pressure'))
      },
      windSpeed () {
        return Math.round(this.resource.attr('wind_speed'))
      },
      windDirection () {
        return formatWindDirection(this.resource.attr('wind_direction'))
      },
      weatherLabel () {
        return this.resource.attr('weather')
      },
      weatherIcon () {
        for (var i in weatherMap) {
            if (this.weatherLabel === weatherMap[i].description) {
                if (weatherMap[i].icon) {
                  var now = new Date()
                  var hours = now.getHours()
                  return toWeatherIcon(weatherMap[i].id, hours >= 21 || hours <= 5)
                  /*
                  var icon;
                  if (Array.isArray(weatherMap[i].icon)) {
                      var now = new Date()
                      var hours = now.getHours()
                      var index = hours >= 21 || hours <= 5 ? 1 : 0
                      icon = weatherMap[i].icon[index]
                  } else {
                      icon = weatherMap[i].icon
                  }
                  return 'img:' + iconPath + '/' + icon + '.' + iconExt*/
                }
                return
            }
        }
      },
    },

    methods: {
      onResize (size) {
        var ratio = size.width / size.height
        this.wide = ratio > 1.5

        this.labels = size.width > 150

        this.details = Math.max(size.width, size.height) > 150

        var size = Math.min(size.width, size.height)
        this.small = size < 150
      }
    }
}

</script>
