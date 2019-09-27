<template>
  <form-schema-layout class="form-schema-google-user-select">

    <q-select
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
              <img :src="scope.opt.account.user.picture">
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ scope.opt.label }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>

      <template v-slot:append>
        <q-icon name="add" class="cursor-pointer" @click.prevent.stop="addGoogleAccountClick" />
      </template>
    </q-select>
  </form-schema-layout>
</template>

<script>

export default {
  name: 'GoogleUserForm',

  mixins: [EThingUI.form.FormComponent],

  data () {
    return {
      accounts: []
    }
  },

  computed: {
    options () {
      return this.accounts.map(account => {
        return {
          value: account.id,
          label: account.user.name || account.name,
          account
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
    load () {
      this.$ething.request('google/accounts').then(accounts => {
        this.accounts = accounts
      })
    },

    addGoogleAccountClick () {
      this.$router.push({name: 'system', params: {panel: 'settings'}})
    },
  },

  mounted () {
    this.load()
  }

}

</script>
