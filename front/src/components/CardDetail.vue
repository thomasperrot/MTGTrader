<template>
    <div class="cardDetail">
        <h1>{{ card.name }}</h1>
        <h2>{{ card.set }}</h2>
    </div>
</template>

<script>
export default {
    name: 'cardDetail',
    data () {
        return {
            card: {
                "id": "958ae1416f8f6287115ccd7c5c61f2415a313546",
                "name": "Abattoir Ghoul",
                "set": "Innistrad"
            }
        }
    }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
    font-weight: normal;
}
</style>
