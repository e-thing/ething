<template>
  <q-page>
    <multipane class="absolute fit custom-resizer" :class="orientation == 'vertical' ? 'vertical-panes' : 'horizontal-panes'" :layout="orientation">
      <div class="pane" :style="orientation == 'vertical' ? { width: '50%', minWidth: '25%', maxWidth: '75%' } : { height: '50%', minHeight: '25%', maxHeight: '75%' }">
        <div class="column absolute fit">
          <div class="col-auto">
            <q-btn-group flat >
              <q-btn :loading="saveLoading" label="save" icon="mdi-content-save-outline" @click="save"/>
              <q-btn :loading="exeLoading" label="run" icon="play_arrow" @click="onExecuteClick"/>
              <q-btn label="settings" icon="settings" @click="settingsModal = true"/>
            </q-btn-group>
            <span class="title text-faded" :class="{dirty: dirty}">{{ resource.name() }}</span>
          </div>
          <q-scroll-area class="col" style="height: 100%">
            <codemirror ref='cm' v-model="content" :options="cmOption" @changes="onChange"></codemirror>
          </q-scroll-area>
        </div>
      </div>
      <multipane-resizer></multipane-resizer>
      <div class="pane console" :style="{ flexGrow: 1 }">
        <div v-if="exeLoading" class="absolute-center text-faded">
          running ...
        </div>
        <q-scroll-area v-else-if="console.enabled" class="absolute fit" ref="outputScrollArea" :content-style="{height: '100%', 'overflow-y': 'auto'}">
          <div class="output">
            <div v-for="(item, key) in console.output" :key="key" class="output-line" :class="item.type">
              <pre class="q-ma-none"><code>{{ item.chunk }}</code></pre>
            </div>
            <div class="output-line info">status: {{ console.info.status ? 'success' : 'fail' }}</div>
            <div class="output-line info">return code: {{ console.info.returnCode }}</div>
            <div class="output-line info" v-if="typeof console.info.executionTime == 'number'">duration: {{ console.info.executionTime }} secondes</div>
          </div>
        </q-scroll-area>
        <div v-else class="absolute-center text-light">
          Console
        </div>
      </div>
    </multipane>

    <modal v-model="settingsModal" title="Settings" icon="settings" valid-btn-hide cancel-btn-label="Close" cancel-btn-color="faded">

      <q-field label="Arguments" class="q-my-md" orientation="vertical">
        <q-input v-model="args" placeholder="--name=value -k --key" />
      </q-field>

    </modal>
  </q-page>
</template>

<script>

import { Multipane, MultipaneResizer } from '../components/vue-multipane';
import { codemirror } from 'vue-codemirror'


export default {
  name: 'PageScript',

  components: {
    codemirror,
    Multipane,
    MultipaneResizer
  },

  data () {
    return {
      content: '',
      cmOption: {
        mode: 'application/javascript',
        tabSize: 4,
        styleActiveLine: true,
        lineNumbers: true,
        lineWrapping: false,
        foldGutter: true,
        styleSelectedText: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        showCursorWhenSelecting: true,
        extraKeys: {
          "Ctrl": "autocomplete",
          "Ctrl-S": () => {
            this.save()
          }
        },
        hintOptions:{
          completeSingle: false
        },
        viewportMargin: Infinity
      },
      loading: true,
      saveLoading: false,
      exeLoading: false,
      dirty: false,
      console: {
        enabled: false,
        output: [],
        info: {}
      },
      orientation: this.$q.platform.is.mobile ? 'horizontal' : 'vertical',
      settingsModal: false,
      args: ''
    }
  },

  computed: {
    resource () {
      var id = this.$route.params.id
      var r = this.$store.getters['ething/get'](id)
      if (id && id.length) {
        if (!r) {
          this.$router.replace('/404')
        }
      }

      return r
    },

  },

  methods: {

    codemirror () {
      return this.$refs['cm'].codemirror
    },

    markClean () {
      this.dirty = false
      this.codemirror().markClean()
    },

    reloadContent () {
      this.loading = true
      this.resource.read().then( (data) => {
        this.content = data
        this.$nextTick(() => {
          this.markClean()
          this.codemirror().clearHistory()
        })
      }).finally( () => {
        this.loading = false
      })
    },

    save (done) {
      this.saveLoading = true
      this.resource.write(this.content).then(() => {
        this.dirty = false
        this.markClean()

        if(typeof done === 'function')
          done()
      }).finally( () => {
        this.saveLoading = false
      })
    },

    onChange (cm, changes) {
      this.dirty = !cm.isClean()
    },

    execute () {
      this.exeLoading = true
      this.resource.execute(this.args).then(result => {
        this.printResult(result)
      }).catch( err => {
        console.error(err)
        this.printResult({
          status: false,
          returnCode: -2
        })
      }).finally(() => {
        this.exeLoading = false
        setTimeout(() => {
          this.$refs.outputScrollArea.setScrollPosition(1000000000)
        }, 1)
      })
    },

    onExecuteClick () {
      this.dirty ? this.save(this.execute) : this.execute()
    },

    printResult (result) {
      this.console.enabled = true
      this.console.output = result.output
      this.console.info = {
        status: result.ok,
        returnCode: result.return_code,
        executionTime: typeof result.executionTime == 'number' ? result.executionTime.toFixed(3) : null
      }
    }
  },

  mounted () {
    // once mounted, we need to trigger the initial server data fetch
    this.reloadContent()
  }

}
</script>

<style lang="stylus">

.vertical-panes > .pane {
  overflow: hidden;
}

.vertical-panes > .pane ~ .pane {
  border-left: 1px solid #ccc;
}

.horizontal-panes > .pane ~ .pane {
  border-top: 1px solid #ccc;
}

.horizontal-panes > .pane {
  overflow: hidden;
}

.custom-resizer > .pane ~ .pane {
}
.custom-resizer > .multipane-resizer {
  background-color: #f1f1f1;
  margin: 0;
  position: relative;
  &:before {
    display: block;
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
  }
  &:hover {
    &:before {
      border-color: #999;
    }
  }
}

.horizontal-panes.custom-resizer > .multipane-resizer {
  top: 0;
  &:before {
    width: 40px;
    height: 3px;
    margin-top: -1.5px;
    margin-left: -20px;
    border-top: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
  }
}

.vertical-panes.custom-resizer > .multipane-resizer {
  left: 0;
  &:before {
    width: 3px;
    height: 40px;
    margin-top: -20px;
    margin-left: -1.5px;
    border-left: 1px solid #ccc;
    border-right: 1px solid #ccc;
  }
}


.console
  .output-line
    padding-left: 16px
    padding-right: 16px

    &.stdout
      color: #777
    &.stderr
      color: #DB2828
    &.info
      color: #1e88e5
    &:not(:last-child)
      border-bottom 1px solid #eee

.CodeMirror
  height 100%

.title.dirty:after
  content '*'
  color #DB2828

</style>
