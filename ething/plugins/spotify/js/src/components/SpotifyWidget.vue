<template>
    <w-layout noFooter :title="r.basename()">


      <div class="fit column items-center gutter-md">
        <div class="col-auto overflow-hidden">
          <div class="row items-center gutter-sm items-center">
            <div class="col-auto">
              <q-select
                v-model="selectedPlaylistId"
               :options="playlistOptions"
              />
            </div>
            <div class="col-auto">
              <q-select
                v-model="selectedDeviceId"
               :options="deviceOptions"
              />
            </div>
            <div class="col-auto">
              <q-btn color="primary" label="play" flat @click="playSelected"/>
            </div>
          </div>
        </div>
        <div class="col-auto text-center">
          <div v-if="currentItem.name" class="text-faded">
            {{ currentItem.name }}
            <span v-if="currentItem.album"> - {{ currentItem.album.name }}</span>
          </div>
          <small v-if="currentDevice.name" class="text-faded">{{ currentDevice.name }}</small>
        </div>
        <div class="col-auto">

          <div class="row items-center gutter-sm items-center">
            <div class="col-auto">
              <span v-if="time" class="text-faded">{{ time }}</span>
            </div>

            <div class="col-auto">
              <q-btn icon="mdi-skip-previous" round @click="prev"/>
              <q-btn :icon="state.is_playing ? 'mdi-pause' : 'mdi-play'" color="primary" round size="xl" @click="playpause"/>
              <q-btn icon="mdi-skip-next" round @click="next"/>
            </div>

            <div class="col-auto">
              <q-btn icon="mdi-volume-low" round size="sm" @click="setVolume('down')"/>
              <q-btn icon="mdi-volume-high" round size="sm" @click="setVolume('up')"/>
            </div>
          </div>
        </div>
      </div>

    </w-layout>
</template>

<script>

import EThingUI from 'ething-quasar-core'
var Spotify = require('spotify-web-api-js');


function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}


export default {
    name: 'WSpotify',

    extends: EThingUI.widgets.WResource,

    components: {
        WLayout: EThingUI.widgets.WLayout
    },

    metadata: {
        label: 'Spotify widget',
        description: 'play music on your device',
        minHeight: 120,
        minWidth: 120
    },

    data () {
        return {
          spotify: new Spotify(),
          devices: [],
          playlists: [],
          selectedDeviceId: null,
          selectedPlaylistId: null,
          refreshing: false,
          state: {
            is_playing: false,
            device: {},
            item: {}
          },
          stateFetchTs: null,
          _currentReq: null,
          _timer: null,
          _cnt: 0,
          time: null
        }
    },

    computed: {

        accessToken () {
          return this.r.attr('access_token')
        },

        playlistOptions () {
          return this.playlists.map(item => {
            return {
              label: item.name,
              value: item.id
            }
          })
        },

        deviceOptions () {
          return this.devices.map(item => {
            return {
              label: item.name,
              value: item.id,
              // icon: item.type
            }
          })
        },

        selectedPlaylist () {
          if (this.selectedPlaylistId) {
            return this.getPlaylistById(this.selectedPlaylistId)
          }
        },

        selectedDevice () {
          if (this.selectedDeviceId) {
            return this.getDeviceById(this.selectedDeviceId)
          }
        },

        currentDevice () {
          return this.state.device || {}
        },

        currentItem () {
          return this.state.item || {}
        },

        currentTrackEstimatedProgress: {
          cache: false,
          get: function () {
            if (!this.stateFetchTs) return 0
            var readProgress = this.state.progress_ms || 0
            var deltaT = Date.now() - this.stateFetchTs
            return readProgress + deltaT
          }
        },

        currentTrackEstimatedProgressPercent () {
          var progress = this.currentTrackEstimatedProgress
          var duration = this.currentItem.duration_ms
          return duration ? (100 * progress / duration) : 0
        }

    },

    watch: {

      'accessToken': {
        handler (val, oldVal) {
          this.spotify.setAccessToken(val)
        },
        immediate: true
      },

    },

    methods: {

        getDeviceById (id) {
          for(var i in this.devices) {
            var device = this.devices[i]
            if (device.id === id) {
              return device
            }
          }
        },

        getPlaylistById (id) {
          for(var i in this.playlists) {
            var playlist = this.playlists[i]
            if (playlist.id === id) {
              return playlist
            }
          }
        },

        refresh () {
          this.refreshing = true

          var p0 = this.spotify.getMyDevices((err, data) => {
            if (err) console.error(err);
            else {
              console.log('Devices:', data);
              this.devices = data.devices

              // get active device
              for(var i in this.devices) {
                if (this.devices[i].is_active) {
                  if (!this.selectedDeviceId) this.selectedDeviceId = this.state.device.id
                  break;
                }
              }
            }
          })

          var p1 = this.spotify.getUserPlaylists((err, data) => {
            if (err) console.error(err);
            else {
              console.log('Playlists:', data);
              this.playlists = data.items
            }
          })

          Promise.all([p0, p1]).finally( () => {
            this.refreshing = false
          })
        },

        prev () {
          this.spotify.skipToPrevious((err, data) => {
            if (err) console.error(err);
            else {
              this.current()
            }
          })
        },

        playpause () {

          if (this.state.is_playing) {
            this.spotify.pause((err, data) => {
              if (err) console.error(err);
              else {
                this.state.is_playing = false
                this.current()
              }
            })
          } else {
            this.spotify.play((err, data) => {
              if (err) console.error(err);
              else {
                this.state.is_playing = true
                this.current()
              }
            })
          }
        },

        next () {
          this.spotify.skipToNext((err, data) => {
            if (err) console.error(err);
            else {
              this.current()
            }
          })
        },

        playSelected () {
          var options = {}

          if (this.selectedPlaylist) {
            options.context_uri = this.selectedPlaylist.uri
          }

          if (this.selectedDevice) {
            options.device_id = this.selectedDevice.id
          }

          if (Object.keys(options).length) {
            this.spotify.play(options, (err, data) => {
              if (err) console.error(err);
              else {
                this.state.is_playing = true
                this.current()
              }
            })
          }
        },

        current () {

          // abort previous request, if any
          if (this._currentReq) {
            this._currentReq.abort();
          }

          this._currentReq = this.spotify.getMyCurrentPlaybackState((err, data) => {

            // clean the promise so it doesn't call abort
            this._currentReq = null;

            if (err) console.error(err);
            else {
              this.stateFetchTs = Date.now()
              Object.assign(this.state, data)
            }
          })

          return this._currentReq
        },

        setVolume (volume) {

          var current_volume = 0

          current_volume = this.currentDevice.volume_percent || 0

          if (volume=='mute') {
            volume = 0
          } else if (volume=='up') {
            volume = current_volume + 5
          }  else if (volume=='down') {
            volume = current_volume - 5
          }

          if (volume < 0) volume = 0
          if (volume > 100) volume = 100

          this.spotify.setVolume(volume, (err, data) => {
            if (err) console.error(err);
            else {
              this.current()
            }
          })
        },

        currentTrackTimeToString () {
          var progress = this.currentTrackEstimatedProgress
          var duration = this.currentItem.duration_ms

          if (duration) {

            function toString (msec) {
              var sec = parseInt(msec / 1000)
              var min = Math.floor(sec / 60)
              sec -= min * 60
              return pad(min, 2) + ":" + pad(sec, 2)
            }

            return toString(progress) + "/" + toString(duration)
          }
        }

    },

    mounted () {
      this._timer = setInterval(() => {

        this._cnt = (this._cnt || 0) + 1

        if ((this._cnt % 5) == 0) {
          this.current()
        }

        if (this.currentTrackEstimatedProgressPercent >= 100) {
          this.current()
        }

        this.time = this.currentTrackTimeToString()

      }, 1000)

      this.current()
      this.refresh()
    },

    beforeDestroy () {
      if(this._timer !== null) {
        clearInterval(this._timer)
      }
    }
}

</script>
