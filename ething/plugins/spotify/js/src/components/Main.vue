<template>
    <div class="absolute fit">
        <div class="relative absolute-center">
            <div v-if="connected">connected</div>
            <q-btn v-else label="connect" color="primary" @click="connect"/>
        </div>
    </div>
</template>

<script>

import EThingUI from 'ething-quasar-core'


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