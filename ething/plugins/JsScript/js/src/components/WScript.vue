<template>
  <div class="column">

    <!--<componant class="col-auto" v-for="(input,index) in inputs" :key="index" :is="input.type" />-->

    <div class="col-auto q-ma-xs text-center" v-for="(input,index) in inputs" :key="index">
      <div class="text-faded">{{ input.name }}</div>
      <componant :is="input.type" v-bind="extractOptions(input)" v-model="args[input.name]"/>
    </div>

    <q-btn class="col" flat :icon="icon" :label="label" :loading="loading" @click="run" color="primary" />
  </div>
</template>

<script>
import EThingUI from 'ething-quasar-core'
import FormSchemaScriptInputItem from './ScriptInput/FormSchemaScriptInputItem'
import scriptInputs from './ScriptInput'
import Vue from 'vue'


EThingUI.form.registerForm(FormSchemaScriptInputItem, schema => {
  if (schema.type === 'script-input-item') {
    return true
  }
})


const defaultLabel = 'run'


export default {
    name: 'WScript',

    mixins: [EThingUI.widgets.WResource],

    components: scriptInputs,

    props: {
      icon: String,
      label: {
        type: String,
        default: defaultLabel
      },
      arguments: String,
      inputs: {
        type: Array,
        default () {
          return []
        }
      }
    },

    data () {
      return {
        loading: false,
        args: {}
      }
    },

    methods: {
      run () {

        var args = this.arguments || ''

        if (this.args) {
          for (var k in this.args) {
            let value = this.args[k]
            if ( typeof value === 'undefined' || value === null || value === '') continue
            args += ' --' + k + '="' + value + '"'
          }
        }

        this.loading = true
        this.r.execute(args).then(result => {
          if (result.ok) {
            this.setError(false)
          } else {
            this.setError('error: ' + result.stderr)
          }
        }).catch((err) => {
          this.setError(err)
        }).finally(() => {
          this.loading = false
        })
      },

      extractOptions (input) {
        var options = Object.assign({}, input)
        delete options.name
        delete options.type
        return options
      }
    },

    metadata: {
      label: 'button',
      minWidth: 50,
      minHeight: 50,
      options: {
        properties: {
          label: {
            type: 'string',
            default: defaultLabel
          },
          arguments: {
            description: 'the arguments to pass to the script',
            type: 'string'
          },
          inputs: {
            description: 'For dynamic arguments add some inputs',
            type: 'array',
            items: {
              description: 'This input will be transmitted to the script (through --<name>=<value>).',
              type: 'script-input-item',
              required: ['name', 'type'],
              properties: {
                name: {
                  type: 'string',
                  minLength: 1
                },
                type: {
                  enum: ['number', 'string']
                }
              }
            },
            _label: function(index, item) {
              return item.name + ' [' + item.type + ']'
            }
          }
        }
      }
    }

}
</script>

<style scoped>
</style>
