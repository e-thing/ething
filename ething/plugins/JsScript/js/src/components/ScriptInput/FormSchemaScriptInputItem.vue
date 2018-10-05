<template>
  <div>
    <small v-if="schema.description" class="form-schema-description">{{ schema.description }}</small>

    <form-schema :schema="rootSchema" v-model="rootModel" @error="rootError = $event"/>

    <div v-if="optionsSchema !== null" class="q-my-md">
      <form-schema :schema="optionsSchema" v-model="optionsModel" @error="optionsError = $event"/>
    </div>

  </div>
</template>

<script>
import inputs from '.'


export default {
  name: 'FormSchemaScriptInputItem',

  mixins: [EThingUI.form.FormComponent],

  data () {

    var options = Object.assign({}, this.model)
    var name = options.name
    var type = options.type

    delete options.name
    delete options.type

    return {
      rootSchema: {
        type: 'object',
        required: ['name', 'type'],
        properties: {
          name: {
            type: 'string',
            minLength: 1,
            pattern: '^[-_0-9a-zA-Z]+$'
          },
          type: {
            enum: Object.keys(inputs)
          }
        }
      },
      rootModel: {
        name,
        type
      },
      rootError: false,
      optionsSchema: null,
      optionsModel: {},
      optionsError: false
    }
  },

  computed: {
    globalError () {
      return this.rootError || this.optionsError
    },
    globalModel () {
      return Object.assign({}, this.rootModel, this.optionsModel)
    },
  },

  watch: {
    globalError: 'setError',
    globalModel: 'setValue',

    'rootModel.type': {
      immediate: true,
      handler (type) {
        var input = type ? inputs[type] : null
        var options = null

        if (input && input.metadata && input.metadata.options)
          options = input.metadata.options

        if (!options || Object.keys(options).length === 0) {
          options = null
        } else {
          options = Object.assign({
            type: 'object'
          }, options)
        }

        this.optionsModel = {}
        this.optionsError = false
        this.optionsSchema = options
      }
    }
  },

}

</script>

<style scoped>

</style>
