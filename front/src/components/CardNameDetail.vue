<template>
    <div class="cardNameDetail">
        <h1>{{ card.name }}</h1>

        <h2>Printings</h2>
        <md-list>
            <md-list-item v-for="printing in card.printings" :key="printing.id">
                <router-link :to="{ name:'CardDetail', params: { cardId: printing.id} }">
                    <div class="md-list-text-container">
                        <span>{{ printing.set }}</span>
                    </div>
                </router-link>
            </md-list-item>
        </md-list>

    </div>
</template>

<script>
export default {
    name: 'cardNameDetail',
    data () {
        return {
            card: {
                "name": "Abattoir Ghoul",
                "printings": [
                    {
                        "set": "Innistrad",
                        "id": "958ae1416f8f6287115ccd7c5c61f2415a313546"
                    },
                    {
                        "set": "Duel Decks: Blessed vs. Cursed",
                        "id": "535cb7b8bc12174fec6caf490f4b2a89f7f4e964"
                    }
                ]
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

a {
    color: #42b983;
}
</style>
