<template>
    <div class="toolbar">
        <md-toolbar>
            <md-button class="md-icon-button" v-on:click.native="$router.push({ name:'Home' })">
                <md-icon>home</md-icon>
            </md-button>
            <md-button v-on:click.native="$router.push({ name:'Tournaments' })">Tournaments</md-button>
            <md-button v-on:click.native="$router.push({ name:'Cards' })">Cards</md-button>
        </md-toolbar>
    </div>
</template>

<script>
export default {
    name: 'toolbar',
    data () {
        return {}
    },
}
</script>
