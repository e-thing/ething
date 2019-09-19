<template>
  <div class="fit scroll">
    <q-list>
      <q-item-label header>{{ feed.title }}</q-item-label>
      <q-item v-for="item in feed.items" :key="item.guid" clickable v-ripple @click="link(item)">
        <q-item-section side v-if="item['media']">
          <q-img
            :src="item['media'].$.url"
            spinner-color="white"
            style="height: 100px; width: 100px"
          />
        </q-item-section>

        <q-item-section>
          <q-item-label>{{ item.title }}</q-item-label>
          <q-item-label caption lines="3">{{ item.contentSnippet }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script>
import EThingUI from 'ething-ui'
import Parser from 'rss-parser'

export default {
    name: 'WGoogleNews',

    extends: EThingUI.components.widgets.Base,

    props: {
      language: String,
      country: String,
    },

    data () {
        return {
          feed: {},
        }
    },

    methods: {

      load () {
        let parser = new Parser({
          customFields: {
            item: [
              ['media:content', 'media'],
            ]
          }
        });

        var q = []
        if (this.language) q.push('hl='+encodeURIComponent(this.language))
        if (this.country) q.push('gl='+encodeURIComponent(this.country))

        return parser.parseURL(this.$ething.toApiUrl('google/news?' + q.join('&'), true)).then(feed => {
          this.feed = feed
        })
      },

      link (item) {
        this.$ethingUI.utils.openURL(item.link)
      },

    },

    mounted () {
        this.load()
    },
}

</script>
