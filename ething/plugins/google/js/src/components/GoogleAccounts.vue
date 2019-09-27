<template>
  <div>
    <q-list bordered v-if="accounts.length>0" class="q-mb-md">
      <q-item v-for="account in accounts" :key="account.id">
        <q-item-section avatar v-if="account.user.picture">
          <q-avatar>
            <img :src="account.user.picture">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label>{{ account.user.name || account.name }}</q-item-label>
          <q-item-label caption lines="1">{{ account.user.email }}</q-item-label>
        </q-item-section>

        <q-item-section side v-show="!account.logged">
          <q-btn flat icon="mdi-login" :label="$q.screen.gt.xs ? 'login' : ''"  @click="login(account)" />
        </q-item-section>

        <q-item-section side>
          <q-btn flat icon="delete" @click="accountDelete(account)" />
        </q-item-section>

      </q-item>
    </q-list>

    <modal v-model="modal" title="Create Google Account" icon="plus" :valid-btn-disable="error" @valid="createAccount(model)">
      <form-schema :schema="schema" v-model="model" @error="error = $event"/>
    </modal>

    <q-btn icon="add" label="add google account" @click="addAccountClick()" />
  </div>
</template>

<script>
export default {
    name: 'GoogleAccounts',
    data () {
      return {
        accounts: [],
        modal: false,
        schema: this.$ethingUI.get('GoogleAccount').schema,
        model: {},
        error: false
      }
    },
    methods: {
      createAccount (data) {
        return this.$ething.request({
          method: 'POST',
          url: 'google/accounts',
          contentType: "application/json; charset=utf-8",
          data
        }).then(account => {
          this.login(account)
        })
      },
      login (account) {
        window.location = this.$ething.toApiUrl('google/login?account=' + account.id, true)
      },
      addAccountClick () {
        this.model = {}
        this.error = false
        this.modal = true
      },
      accountDelete (account) {
        return this.$ething.request({
          method: 'DELETE',
          url: 'google/accounts/' + account.id,
        }).then(() => {
          return this.load()
        })
      },
      load () {
        return this.$ething.request('google/accounts').then(accounts => {
          this.accounts = accounts
        })
      }
    },
    mounted () {
        this.load()
    },
}
</script>
