<template>
  <div>
    <q-list bordered v-if="users.length>0" class="q-mb-md">
      <q-item v-for="user in users" :key="user.id">
        <q-item-section avatar>
          <q-avatar>
            <img :src="user.picture">
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label>{{ user.name }}</q-item-label>
          <q-item-label caption lines="1">{{ user.email }}</q-item-label>
        </q-item-section>

        <q-item-section side>
          <q-btn flat icon="logout" :label="$q.screen.gt.xs ? 'logout' : ''" @click="googleAccountLogoutClick(user)" />
        </q-item-section>

      </q-item>
    </q-list>

    <q-btn icon="add" label="add google account" @click="addGoogleAccountClick" />
  </div>
</template>

<script>
import EThingUI from 'ething-ui'


export default {
    name: 'WGoogleAccounts',

    extends: EThingUI.components.widgets.Base,

    data () {
        return {
          users: []
        }
    },

    methods: {

      addGoogleAccountClick () {
        window.location = this.$ething.toApiUrl('google/login', true)
      },

      googleAccountLogoutClick (user) {
        this.$ething.request('google/logout/'+user.id)
      }

    },

    mounted () {
        this.$ething.request('google/users').then(users => {
          this.users = users
        })
    },
}

</script>
