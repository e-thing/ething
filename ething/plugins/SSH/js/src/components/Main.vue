<template>
    <div>
      <div v-if="!shell" class="text-center">
        <div>
          <q-btn label="new connection" icon="add" flat color="primary" @click="open()"/>
        </div>
        <div v-for="shell in shells" :key="shell.id">
          <q-btn :label="shell.id" icon="mdi-console" flat color="faded" @click="open(shell.id)"/>
        </div>
      </div>
      <div v-else class="text-right">
        <q-btn label="close terminal" flat color="faded" icon="mdi-close-box-outline" @click="close"/>
      </div>
      <div ref="term"></div>
    </div>
</template>

<script>

import EThingUI from 'ething-quasar-core'
import {InteractiveShell} from '../shell'
import { Terminal } from 'xterm'
import 'xterm/dist/xterm.css'


export default {

    props: ['resource'],

    data () {
        return {
          shell: null,
          term: null,
          shells: []
        }
    },

    computed: {
      shell_status () {
        return this.shell.state
      }
    },

    methods: {
        open (shell_id) {

          var shell = new InteractiveShell(this.resource, shell_id)
          var term = null
          var buffer = ''

          shell.ondata = (data) => {
            // convert arraybuffer into str
            data = String.fromCharCode.apply(null, new Uint8Array(data))

            if (!this.term) {
              buffer += data
            } else {
              this.term.write(data);
            }
          }

          shell.onopen = () => {
            term = this.term = new Terminal({
        			cols: 80,
        			rows: 24,
        			/*useStyle: true,
        			screenKeys: true*/
        		});

            term.on('data', (data) => {
        			shell.send(data);
        		});

            // mount
            term.open(this.$refs.term)

            if (buffer) {
              this.term.write(buffer);
              buffer = ''
            }
          }

          shell.onclose = () => {
            if (term) {
              term.destroy()
              shell.destroy()
              this.term = null
              this.shell = null
              this.list_available_shells()
            }
          }

          this.shell = shell

          shell.open()
        },

        close () {
          if (this.shell) {
            this.shell.close()
          }
        },

        list_available_shells () {
          this.$ething.request('/ssh/shells').then(shells => {
            console.log(shells)
            this.shells = shells.filter(shell => shell.device_id === this.resource.id())
          })
        }

    },

    mounted () {
      this.list_available_shells()
    },

    beforeDestroy () {
      if (this.shell) {
        this.shell.destroy()
      }
      if (this.term) {
        this.term.destroy()
      }
    }

}

</script>
