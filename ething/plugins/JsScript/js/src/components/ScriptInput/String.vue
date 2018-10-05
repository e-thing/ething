<template>
  <q-input type="text" placeholder="input..." :value="value" @input="$emit('input', $event)" v-bind="$attrs"/>
</template>

<script>

export default {
  name: 'StringInput',

  props: ['value']

}

</script>
