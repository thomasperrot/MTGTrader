<template>
    <div class="tournamentDetail">

        <md-list>
            <md-list-item class="md-inset" v-for="deck in tournament.decks" :key="deck.deck_id">

                <span>{{ deck.position }} - <span>{{ deck.deck_name }}</span></span>

                <md-button class="md-icon-button" @click.native="showDeck(deck.deck_id)">
                    <md-icon>keyboard_arrow_right</md-icon>
                </md-button>

            </md-list-item>
        </md-list>
    </div>
</template>

<script>
export default {
    name: 'tournamentDetail',
    props: ['tournamentId', 'clickedDeck'],
    computed: {
        computedId: function () {
            if ( this.tournamentId != null ) {
                return this.tournamentId
            }
            return '';
        }
    },
    data: function() {
        this.tournament = {};
        return {
            tournament: this.tournament,
            internalClickedDeck: ''
        }
    },
    methods: {
        showDeck: function(deckId) {
            this.internalClickedDeck = deckId;
            this.$emit('update:clickedDeck', this.internalClickedDeck)
        }
    },

    created: function(){
        var url = 'http://localhost:8000/mtgtrader/tournaments/' + this.tournamentId
        this.$http.get(url).then(response => {
            this.tournament = response.body;
        }, response => {
            (function(){})
        });
        this.internalClickedDeck = this.clickedDeck
    },
}
</script>
