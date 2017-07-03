<template>
    <div class="tournaments">

        <md-layout md-gutter>
            <md-layout md-column md-gutter md-flex="40">
                <md-list>
                    <md-list-item v-for="tournament in tournaments_data.results" :key="tournament.id">
                        <md-icon class="md-primary">star</md-icon>
                        <div class="md-list-text-container">
                            <span>{{ tournament.name }} - {{ tournament.event_date }}</span>
                        </div>
                        <md-list-expand>
                            <tournament-detail :tournament-id="tournament.id" :clicked-deck.sync="clickedDeck"></tournament-detail>
                        </md-list-expand>
                    </md-list-item>
                </md-list>
            </md-layout>

            <md-layout md-column md-gutter v-if="clickedDeck != ''">
                <deck-detail :deck-id="clickedDeck"></deck-detail>
            </md-layout>
            <md-layout md-column md-gutter v-else>
                Click on a deck to display it
            </md-layout>
        </md-layout>

    </div>
</template>

<script>
import tournamentDetail from './TournamentDetail.vue'
import deckDetail from './DeckDetail.vue'

export default {
    name: 'tournaments',
    components: {
        'tournament-detail': tournamentDetail,
        'deck-detail': deckDetail
    },
    filters: {
        capitalize: function (value) {
            if (!value) return ''
            value = value.toString()
            return value.charAt(0).toUpperCase() + value.slice(1)
        }
    },

    mounted: function(){
        this.$http.get('http://localhost:8000/mtgtrader/tournaments/').then(response => {
            this.tournaments_data.results = response.body.results;
        }, response => {
            (function(){})
        });
    },

    data: function() {
        this.tournaments_data = {
            "results": [],
            "tournamentId": "",
            "clickedDeck": "",
        };
        return this.tournaments_data
    }
}
</script>
