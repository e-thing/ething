<template>

      <div class="fit column justify-center items-stretch">
        <div class="col-auto overflow-hidden q-ma-md">
          <div class="row gutter-sm items-center">
            <div class="col">
              <q-select
                v-model="selectedPlaylistId"
               :options="playlistOptions"
               placeholder="playlist"
              />
            </div>
            <div class="col">
              <q-select
                v-model="selectedDeviceId"
               :options="deviceOptions"
               placeholder="device"
              />
            </div>
            <div class="col-auto">
              <q-btn color="primary" label="play" @click="playSelected"/>
            </div>
          </div>
        </div>
        <div class="col-auto text-center q-ma-md">
          <div v-if="currentItem.name" class="text-faded ellipsis">
            {{ currentItem.name }}
            <span v-if="currentItem.album"> - {{ currentItem.album.name }}</span>
          </div>
          <small v-if="currentDevice.name" class="text-faded">{{ currentDevice.name }}</small>
        </div>
        <div class="col-auto q-ma-md">

          <div class="row gutter-sm items-center">
            <div class="col text-right">
              <span v-if="time" class="text-faded">{{ time }}</span>
            </div>

            <div class="col-auto">
              <q-btn icon="mdi-skip-previous" round @click="prev"/>
              <q-btn :icon="state.is_playing ? 'mdi-pause' : 'mdi-play'" color="primary" round size="xl" @click="playpause"/>
              <q-btn icon="mdi-skip-next" round @click="next"/>
            </div>

            <div class="col">
              <q-btn icon="mdi-shuffle-variant" :color="state.shuffle_state ? 'primary' : ''" round size="sm" @click="setShuffle(!state.shuffle_state)"/>
              <q-btn icon="mdi-repeat" :color="state.repeat_state=='off' ? '' : 'primary'" round size="sm" @click="setRepeat(state.repeat_state=='off'?'context':'off')"/>
              <q-btn icon="mdi-volume-low" round size="sm" @click="setVolume('down')"/>
              <q-btn icon="mdi-volume-high" round size="sm" @click="setVolume('up')"/>
            </div>
          </div>
        </div>
      </div>

</template>

<script>

import EThingUI from 'ething-ui'
var Spotify = require('spotify-web-api-js');


function pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}


export default {
    name: 'WSpotify',

    extends: EThingUI.components.widgets.WResource,

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
            item: {},
            shuffle_state: false,
            repeat_state: false
          },
          stateFetchTs: null,
          p_currentReq: null,
          p_timer: null,
          p_cnt: 0,
          time: null,
          p_observer: null
        }
    },

    computed: {

        accessToken () {
          return this.resource.attr('access_token')
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
            var deltaT = this.state.is_playing ? (Date.now() - this.stateFetchTs) : 0
            return readProgress + deltaT
          }
        },

        currentTrackEstimatedProgressPercent () {
          var progress = this.currentTrackEstimatedProgress
          var duration = this.currentItem.duration_ms
          return duration ? (100 * progress / duration) : 0
        },

        pollingActivated () {
          return this.p_timer !== null
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
              this.current(true)
            }
          })
        },

        playpause () {

          if (this.state.is_playing) {
            this.spotify.pause((err, data) => {
              if (err) console.error(err);
              else {
                this.state.is_playing = false
                this.current(true)
              }
            })
          } else {
            this.spotify.play((err, data) => {
              if (err) console.error(err);
              else {
                this.state.is_playing = true
                this.current(true)
              }
            })
          }
        },

        next () {
          this.spotify.skipToNext((err, data) => {
            if (err) console.error(err);
            else {
              this.current(true)
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
                this.current(true)
              }
            })
          }
        },

        _current () {

          // abort previous request, if any
          if (this.p_currentReq) {
            this.p_currentReq.abort();
          }

          this.p_currentReq = this.spotify.getMyCurrentPlaybackState((err, data) => {

            // clean the promise so it doesn't call abort
            this.p_currentReq = null;

            if (err) console.error(err);
            else {
              this.stateFetchTs = Date.now()
              Object.assign(this.state, data)
            }
          })

          return this.p_currentReq
        },

        current (delay) {
          if (delay) {
            setTimeout(() => {
              this._current()
            }, 500)
          } else {
            this._current()
          }
        },

        setShuffle (state) {
          state = !!state
          this.spotify.setShuffle(state, (err, data) => {
            if (err) console.error(err);
            else {
              this.$set(this.state, 'shuffle_state', state)
              this.current(true)
            }
          })
        },

        setRepeat (state) {
          this.spotify.setRepeat(state, (err, data) => {
            if (err) console.error(err);
            else {
              this.$set(this.state, 'repeat_state', state)
              this.current(true)
            }
          })
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
              if (this.state.device) {
                this.$set(this.state.device, 'volume_percent', volume)
              }
              this.current(true)
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

            if (progress > duration) progress = duration

            return toString(progress) + "/" + toString(duration)
          }
        },

        _installPolling () {
          if (this.p_timer === null) {
            this.current()
            this.p_cnt = 0
            this.p_timer = setInterval(this._pollFunc, 1000)
          }
        },

        _uninstallPolling () {
          if(this.p_timer !== null) {
            clearInterval(this.p_timer)
            this.p_timer = null
          }
        },

        _pollFunc () {
          this.p_cnt = (this.p_cnt || 0) + 1

          if ((this.p_cnt % 5) == 0) {
            this.current()
          }

          if (this.currentTrackEstimatedProgressPercent >= 100) {
            this.current()
          }

          this.time = this.currentTrackTimeToString()
        }

    },

    mounted () {

      this._installPolling()

      this.refresh()

      this.p_observer = new EThingUI.utils.VisibilityObserver((visible, reason) => {
        if (visible) {
          this._installPolling()
        } else {
          this._uninstallPolling()
        }
      }, this.$el, {
        'waitHidden': 10000
      })
    },

    beforeDestroy () {
      if (this.p_observer) {
        this.p_observer.destroy()
      }

      this._uninstallPolling()
    }
}

</script>
