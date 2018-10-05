<template>
  <q-knob :value="value" @input="$emit('input', $event)" v-bind="$attrs" label color="primary"/>
</template>

<script>

export default {
  name: 'KnobInput',

  props: {
    value: {
      default: 0
    }
  },

  metadata: {
    options: {
      properties: {
        min: {
          type: 'number',
          required: true
        },
        max: {
          type: 'number',
          required: true
        },
      }
    }
  }

}

</script>
