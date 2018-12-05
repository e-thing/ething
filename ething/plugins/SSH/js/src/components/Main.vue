<template>
    <div>
      <div v-if="!shell" class="text-center">
        <div>
          <q-btn label="new connection" icon="add" flat color="primary" @click="open()"/>
        </div>
      </div>
      <div v-else class="text-right">
        <q-btn label="close terminal" flat color="faded" icon="mdi-close-box-outline" @click="close"/>
      </div>
      <div v-if="shell_status==='opening' || shell_status==='closing'" class="text-center text-faded">
        {{ shell_status }}
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
          shells: [],
          dbKey: 'shell_' + this.resource.id(),
          dbType: 'session'
        }
    },

    computed: {
      shell_status () {
        return this.shell ? this.shell.state : 'none'
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
            this.$ethingUI.dbSet(this.dbKey, shell.id, this.dbType)

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
            this.$ethingUI.dbDelete(this.dbKey, this.dbType)
            if (term) {
              term.destroy()
              shell.destroy()
              this.term = null
              this.shell = null
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
          return this.$ething.request('/ssh/shells').then(shells => {
            console.log(shells)
            this.shells = shells.filter(shell => shell.device_id === this.resource.id())
          })
        },

        get_shell_info (shell_id) {
          return this.$ething.request('/ssh/shells/'+shell_id)
        }

    },

    mounted () {

      // check for opened terminal
      var shell_id = this.$ethingUI.dbGet(this.dbKey, this.dbType)
      if (shell_id) {
        // check if the shell still exist
        this.get_shell_info(shell_id).then(shell => {
          this.open(shell_id)
        }).catch(() => {})
      }
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
