<template>
  <q-color :value="value" @input="$emit('input', $event)" v-bind="$attrs"/>
</template>

<script>

export default {
  name: 'ColorInput',

  props: ['value']

}

</script>
