<template>
  <div class="fit">
    <q-resize-observer @resize="onResize" />

    <div v-if="__layout=='xs'" class="fit relative-position">
      <q-img
          :src="image_url"
          :ratio="1"
          class="fit"
        />
      <div class="absolute-bottom full-width">
        <q-btn-group spread stretch flat>
          <q-btn icon="mdi-skip-previous" @click="prev()" />
          <q-btn :icon="resource.attr('state')=='playing' ? 'mdi-pause' : 'mdi-play'" @click="toggle()" />
          <q-btn icon="mdi-skip-next" @click="next()"/>
        </q-btn-group>
      </div>
    </div>
    <template v-else>
      <div class="row">
        <div class="col-auto">
          <q-img
              :src="image_url"
              :ratio="1"
              :style="__imgStyle"
            />
        </div>

        <div class="col column">
            <div class="col q-px-sm full-width">
              <div class="text-h5 ellipsis">{{ __title }}</div>
              <div class="text-subtitle1 row no-wrap q-gutter-x-sm items-center">
                <q-icon class="col-auto" name="mdi-artist"/>
                <span class="col-auto ellipsis" style="max-width: 250px;">{{ __artist }}</span>
                <span class="col-auto"> - </span>
                <q-icon class="col-auto"name="mdi-album"/>
                <span class="col ellipsis">{{ __album }}</span>
              </div>
              <div class="text-subtitle1 ellipsis" v-show="height>150"><q-icon name="mdi-speaker" style="vertical-align: baseline;" class="q-mr-sm"/>{{ resource.attr('current_device') }}</div>
            </div>
            <div class="col-auto">
              <q-btn-group spread stretch flat>
                <q-btn icon="mdi-skip-previous" @click="prev()" />
                <q-btn :icon="resource.attr('state')=='playing' ? 'mdi-pause' : 'mdi-play'" @click="toggle()" />
                <q-btn icon="mdi-skip-next" @click="next()"/>
                <div class="row">
                  <q-btn icon="mdi-volume-minus" flat @click="volume(__volume-10)"/>
                  <div class="q-pt-sm">
                    {{ __volume }}%
                  </div>
                  <q-btn icon="mdi-volume-plus" flat @click="volume(__volume+10)"/>
                </div>
              </q-btn-group>
            </div>
        </div>
      </div>
      <div v-if="__layout!='wide'" class="row">
        <q-scroll-area :style="{height: (height - __imgSize) + 'px'}" :class="context ? 'col-6' : 'col-12'">
          <q-list>
            <q-item-label header>Playlists</q-item-label>
            <q-item
              v-for="item in playlists"
              :key="item.id"
              clickable
              v-ripple
              @click="play(item.uri)"
              :active="item.uri === __contextUri"
              active-class="text-orange"
            >
              <q-item-section top avatar>
                <q-avatar rounded>
                  <img :src="item.imageUrl">
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ item.name }}</q-item-label>
                <q-item-label caption>{{ item.owner }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-scroll-area>
        <q-scroll-area :style="{height: (height - __imgSize) + 'px'}" class="col-6" v-if="context">
          <q-list>
            <q-item-label header>Tracks</q-item-label>
            <q-item
              v-for="item in context.tracks"
              :key="item.id"
              clickable
              v-ripple
              @click="item.play()"
              :active="item.name === __title"
              active-class="text-orange"
            >
              <q-item-section top avatar>
                <q-avatar rounded>
                  <img :src="item.imageUrl">
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ item.name }}</q-item-label>
                <q-item-label caption>{{ item.artists }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-scroll-area>
      </div>
    </template>

  </div>

</template>

<script>

import EThingUI from 'ething-ui'


export default {
    name: 'WSpotify',

    extends: EThingUI.components.widgets.Base,

    data () {
        return {
          height: 32,
          width: 32,
          playlists: [],
          context: null,
          contextData: null
        }
    },

    computed: {

        image_url () {
          return this.resource.attr('image_url')
        },

        __layout () {
          if (this.width < 300) {
            return 'xs'
          } else {
            if (this.width > 3*this.height && this.height < 300) {
              return 'wide'
            } else {

            }
          }
        },

        __imgSize () {
          return this.__layout === 'wide' ? this.height : 130
        },

        __imgStyle () {
          return {
            height: this.__imgSize + 'px',
            width: this.__imgSize + 'px',
          }
        },

        __title () {
          return this.resource.attr('title')
        },

        __album () {
          return this.resource.attr('album')
        },

        __artist () {
          return this.resource.attr('artist')
        },

        __volume () {
          return this.resource.attr('volume')
        },

        __contextUri () {
          if (this.contextData) return this.contextData.uri
        },

    },

    watch: {
      __title: {
        handler (val) {
          if (val) {
            // get context
            this.loadContext()
          } else {
            // remove context
            this.context = null
          }
        },
        immediate: true
      },
      __contextUri: {
        handler (uri) {
          if (uri) {
            // update context
            var contextData = this.contextData;
            if (contextData.type === 'playlist') {
              this.loadPlaylistInfo(contextData.uri).then(playlistData => {
                this.context = Object.assign(contextData, {
                  tracks: playlistData.tracks.items.map(trackItemData => trackItemData.track).map(item => {
                    var imageUrl = null, artists = null;
                    if (item.album && item.album.images && item.album.images.length>0) {
                      imageUrl = item.album.images[0].url
                    }
                    if (item.artists) {
                      artists = item.artists.map(artist => artist.name).join(', ')
                    }
                    return {
                      imageUrl,
                      artists,
                      name: item.name,
                      id: item.id,
                      uri: item.uri,
                      play: () => {
                        this.play(contextData.uri, {
                          uri: item.uri
                        })
                      }
                    }
                  })
                })
              })
            } else {
              this.context = null
            }
          }
        },
        immediate: true
      },
    },

    methods: {
      onResize (size) {
        this.height = size.height
        this.width = size.width
      },

      prev () {
        return this.resource.execute('previous_track').catch(err => {

        })
      },

      next () {
        return this.resource.execute('next_track').catch(err => {

        })
      },

      toggle () {
        return this.resource.execute(this.resource.attr('state')=='playing' ? 'pause_playback' : 'start_playback').catch(err => {

        })
      },

      loadPlaylists () {
        return this.resource.execute('current_user_playlists', {limit: 20}).then(playlists => {
          this.playlists = playlists.items.map(item => {
            var imageUrl = null;
            if (item.images && item.images.length>0) {
              imageUrl = item.images[0].url
            }
            return {
              imageUrl,
              owner: item.owner.display_name,
              name: item.name,
              id: item.id,
              uri: item.uri
            }
          })
        }).catch(err => {

        })
      },

      play (uri, offset) {
        return this.resource.execute('start_playback', {
          context_uri: uri,
          offset: offset
        }).catch(err => {

        })
      },

      loadContext () {
        return this.resource.execute('current_playback').then(data => {
          this.contextData = data.context
        }).catch(err => {

        })
      },

      loadPlaylistInfo (playlistId) {
        return this.resource.execute('current_user_playlist', {
          playlist_id: playlistId.split(':').pop()
        }).catch(err => {

        })
      },

      volume (vol) {
        if (vol < 0) vol = 0;
        if (vol > 100) vol = 100;

        return this.resource.execute('set_volume', {
          volume_percent: vol
        }).catch(err => {

        })
      }

    },

    mounted () {
      this.loadPlaylists()
    },
}

</script>
