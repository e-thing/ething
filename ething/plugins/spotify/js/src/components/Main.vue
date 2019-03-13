<template>
    <div class="text-center">
        <span v-if="connected">connected</span>
        <q-btn v-else label="connect" color="primary" @click="connect"/>
    </div>
</template>

<script>

import EThingUI from 'ething-ui'


export default {

    props: ['resource'],

    data () {
        return {}
    },

    computed: {

        connected () {
            return !!this.resource.attr('access_token')
        }

    },

    methods: {

        connect () {

            window.location = this.$ething.toApiUrl('resources/'+this.resource.id()+'/spotify/login?redirect_uri=' + encodeURIComponent(window.location))

        }

    }

}

</script>
