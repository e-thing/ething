<template>
  <div class="fit scroll">

    <resource-observable :resource="this.resource" attribute="contentModifiedDate" @change="load()"/>

    <q-list>
      <template v-for="(daily, index) in dailyEvents">
        <q-separator v-if="index>0" />
        <q-item-label header class="q-py-sm">{{ daily.date }}</q-item-label>
        <q-item v-for="event in daily.events" :key="event.id" clickable v-ripple @click="link(event)">
          <q-item-section class="text-white col-auto q-px-md text-center" style="min-width: 100px;" :style="{backgroundColor: color}">
            <q-item-label>{{ formatTime(event) }}</q-item-label>
          </q-item-section>

          <q-item-section>
            <q-item-label>{{ event.summary }}</q-item-label>
            <q-item-label caption lines="2" v-if="event.description">{{ event.description }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-list>
  </div>
</template>

<script>
import EThingUI from 'ething-ui'


export default {
    name: 'WGoogleCalendar',

    extends: EThingUI.components.widgets.Base,

    data () {
        return {
          events: [],
        }
    },

    computed: {
      dailyEvents () {
        var prevDate = null
        var dailyData = []
        this.events.forEach(event => {
          var date = this.$ethingUI.utils.date.formatDate(event.start.dateTime || event.start.date, 'dddd, MMMM D')
          if (date !== prevDate) {
            prevDate = date
            dailyData.push({
              date,
              events: []
            })
          }
          dailyData[dailyData.length-1].events.push(event)
        })
        return dailyData
      }
    },

    methods: {

      load () {
        return this.resource.execute('list_events', events => {
          this.events = events || []
        })
      },

      link (event) {
        this.$ethingUI.utils.openURL(event.htmlLink)
      },

      formatTime (event) {
        if (event.start.date) return "all day"
        return this.$ethingUI.utils.date.formatDate(event.start.dateTime, 'HH:mm')
      }

    },

    mounted () {
        this.load()
    },
}

</script>
