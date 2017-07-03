<template>
    <div class="deckDetail">

        <span class="md-title">{{ deck.name }}</span>
        <span class="md-subheading">{{ deck.owner}}</span>

        <md-tabs md-fixed v-show="deckIsLoaded">
            <md-tab id="main-deck" md-label="Main deck">
                <md-layout md-gutter>
                    <!--<md-layout md-column md-gutter>-->
                        <md-layout>
                            <!--<span class="md-subheading">Lands</span>-->
                            <md-list>
                                <md-list-item v-for="card in deck.cards.main_deck.lands" :key="card.card_name">
                                    <router-link :to="{ name:'CardNameDetail', params: { cardName: card.card_name} }">
                                        <div class="md-list-text-container">
                                            <span>{{ card.number }} - {{ card.card_name }}</span>
                                        </div>
                                    </router-link>
                                </md-list-item>
                            </md-list>
                        </md-layout>

                        <md-layout>
                            <!--<span class="md-subheading">Creatures</span>-->
                            <md-list>
                                <md-list-item v-for="card in deck.cards.main_deck.creatures" :key="card.card_name">
                                    <router-link :to="{ name:'CardNameDetail', params: { cardName: card.card_name} }">
                                        <div class="md-list-text-container">
                                            <span>{{ card.number }} - {{ card.card_name }}</span>
                                        </div>
                                    </router-link>
                                </md-list-item>
                            </md-list>
                        </md-layout>
                    <!--</md-layout>-->

                    <!--<md-layout md-column md-gutter>-->
                        <md-layout>
                            <!--<span class="md-subheading">Instants and sorc.</span>-->
                            <md-list>
                                <md-list-item v-for="card in deck.cards.main_deck.instants_and_sorceries" :key="card.card_name">
                                    <router-link :to="{ name:'CardNameDetail', params: { cardName: card.card_name} }">
                                        <div class="md-list-text-container">
                                            <span>{{ card.number }} - {{ card.card_name }}</span>
                                        </div>
                                    </router-link>
                                </md-list-item>
                            </md-list>
                        </md-layout>

                        <md-layout>
                            <!--<span class="md-subheading">Others</span>-->
                            <md-list>
                                <md-list-item v-for="card in deck.cards.main_deck.other_spells" :key="card.card_name">
                                    <router-link :to="{ name:'CardNameDetail', params: { cardName: card.card_name} }">
                                        <div class="md-list-text-container">
                                            <span>{{ card.number }} - {{ card.card_name }}</span>
                                        </div>
                                    </router-link>
                                </md-list-item>
                            </md-list>
                        </md-layout>

                    <!--</md-layout>-->
                </md-layout>
            </md-tab>


            <md-tab id="sideboard" md-label="Sideboard">
                <md-layout md-gutter>
                    <md-list>
                        <md-list-item v-for="card in deck.cards.sideboard" :key="card.card_name">
                            <router-link :to="{ name:'CardNameDetail', params: { cardName: card.card_name} }">
                                <div class="md-list-text-container">
                                    <span>{{ card.number }} - {{ card.card_name }}</span>
                                </div>
                            </router-link>
                        </md-list-item>
                    </md-list>
                </md-layout>
            </md-tab>
        </md-tabs>

        <md-tabs md-fixed v-show="!deckIsLoaded">
            <md-tab id="main-deck-spin" md-label="Main deck">
                <md-spinner md-indeterminate></md-spinner>
            </md-tab>
            <md-tab id="sideboard-spin" md-label="Sideboard">
                <md-spinner md-indeterminate></md-spinner>
            </md-tab>
        </md-tabs>

    </div>
</template>

<script>
export default {
    name: 'deckDetail',
    props: ['deckId'],
    data() {
        return {
            deck: {
                'cards': {
                    'main_deck': {
                        'lands': [],
                        'creatures': [],
                        'instants_and_sorceries': [],
                        'others': []
                    },
                    'sideboard': []
                }
            }
        }
    },
    mounted(){
        this.query_api(this.deckId)
    },
    computed: {
        deckIsLoaded() {
            let main_deck = this.deck.cards.main_deck
            for (let section in main_deck) {
                if (main_deck.hasOwnProperty(section)) {
                    if (main_deck[section].length > 0) {
                        return true
                    }
                }
            }
            return false
        },
    },
    watch: {
        deckId(newValue, oldValue) {
            this.deck = {
                'cards': {
                    'main_deck': {
                        'lands': [],
                        'creatures': [],
                        'instants_and_sorceries': [],
                        'others': []
                    },
                    'sideboard': []
                }
            }
            this.query_api(newValue)
        }
    },
    methods: {
        query_api(deckId) {
            let url = 'http://localhost:8000/mtgtrader/decks/' + deckId;
            this.$http.get(url).then(response => {
                this.deck = response.body
            }, response => {
                {()=>{}}
            });
        }
    },

}
</script>
