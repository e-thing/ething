<template>
  <form-schema-layout class="form-schema-google-user-select">

    <select
      v-model="model"
      :error="!!error"
      hide-bottom-space
      empty-message="no account registered"
      :options="options"
    >
      <template v-slot:option="scope">
        <q-item
          v-bind="scope.itemProps"
          v-on="scope.itemEvents"
        >
          <q-item-section avatar>
            <q-avatar>
              <img :src="scope.opt.user.picture">
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ scope.opt.user.name }}</q-item-label>
            <q-item-label caption lines="1">{{ scope.opt.user.email }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>

      <template v-slot:append>
        <q-icon name="add" class="cursor-pointer" @click.prevent.stop="addGoogleAccountClick" />
      </template>
    </select>
  </form-schema-layout>
</template>

<script>

export default {
  name: 'GoogleUserForm',

  mixins: [EThingUI.form.FormComponent],

  data () {
    return {
      users: []
    }
  },

  computed: {
    options () {
      return this.users.map(user => {
        return {
          value: user.id,
          label: user.name,
          user
        }
      })
    },
    model: {
      get: function () {
        for (var i in this.options) {
          if (this.options[i].value === this.c_value) {
            return this.options[i]
          }
        }
      },
      set: function (val) {
        this.c_value = val ? val.value : null
      }
    },
  },

  methods: {
    listUsers () {
      this.$ething.request('google/users').then(users => {
        this.users = users
      })
    },

    addGoogleAccountClick () {
      window.location = this.$ething.toApiUrl('google/login', true)
    },
  },

  mounted () {
    this.listUsers()
  }

}

</script>
