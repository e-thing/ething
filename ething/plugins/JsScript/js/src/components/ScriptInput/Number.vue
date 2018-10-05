<template>
  <q-input type="number" placeholder="input..." :value="value" @input="$emit('input', $event)" v-bind="$attrs"/>
</template>

<script>

export default {
  name: 'NumberInput',

  props: ['value'],

  metadata: {
    options: {
      properties: {
        min: {
          type: 'number'
        },
        max: {
          type: 'number'
        },
      }
    }
  }

}

</script>
