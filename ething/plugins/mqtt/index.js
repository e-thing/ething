(function(global){

    function deepCopy(obj) {
        return JSON.parse(JSON.stringify(obj))
    }


    EThingUI.extend('resources/MQTT', {

        properties: {

            subscription: {
                description: 'Subscribe to topics and store information contained in the incoming messages',
                type: 'array',
                items: {
                    type: 'mqtt-sub-item'
                }
            }
        }

    })


    var rootSchema = {
        type: 'object',
        required: ['name', 'topic', 'type'],
        properties: {
            name: {
              type: 'string',
              minLength: 1,
              pattern: '^[-_0-9a-zA-Z]+$'
            },
            topic: {
              type: 'string',
              minLength: 1,
            },
            type: {
              enum: ['JSON', 'XML', 'text'],
            }
        }
    }

    var FormSchemaMqttSubItem = {
        name: 'FormSchemaMqttSubItem',

        template: '<div><small v-if="schema.description" class="form-schema-description">{{ schema.description }}</small><form-schema :schema="rootSchema" :model="internalModel" @input="setInternalValue" @error="setError"/></div>',

        mixins: [EThingUI.form.FormComponent],

        data () {
            return {
              rootSchema: deepCopy(rootSchema),
            }
        },

        computed: {

            internalModel () {
              var copy = Object.assign({}, this.model)

              if (typeof copy.jsonPath !== 'undefined') {
                copy.type = 'JSON'
              } else if (typeof copy.xpath !== 'undefined') {
                copy.type = 'XML'
              } else {
                copy.type = 'text'
              }

              //console.log('internalModel', copy)

              return copy
            },
        },

        watch: {

            'internalModel.type': {
              immediate: true,
              handler (type) {

                var filter = {
                  type: 'string',
                  minLength: 1,
                  required: true
                }

                var orig = deepCopy(rootSchema)

                //console.log('rootModel.type', orig)

                if (type === 'JSON') {
                  orig.properties['jsonPath'] = filter
                } else if (type === 'XML') {
                  orig.properties['xpath'] = filter
                } else {
                  orig.properties['regexp'] = filter
                }

                this.rootSchema = orig
              }
            }
        },

        methods: {
            setInternalValue (value) {
              // remove the type eattributes
              var copy = Object.assign({}, value)
              var type = copy.type
              delete copy.type

              if (type === 'JSON') {
                copy.jsonPath = copy.jsonPath || ''
                delete copy.xpath
                delete copy.regexp
              } else if (type === 'XML') {
                copy.xpath = copy.xpath || ''
                delete copy.jsonPath
                delete copy.regexp
              } else {
                copy.regexp = copy.regexp || ''
                delete copy.jsonPath
                delete copy.xpath
              }

              //console.log('setInternalValue', copy)

              this.setValue(copy)
            }
        }

    }

    EThingUI.form.registerForm(FormSchemaMqttSubItem, schema => {
        if (schema.type === 'mqtt-sub-item') {
            return true
        }
    })



})(this);