import Vue from 'vue'
import Router from 'vue-router'
import Tournaments from '@/components/Tournaments'
import TournamentDetail from '@/components/TournamentDetail'
import DeckDetail from '@/components/DeckDetail'
import CardNameDetail from '@/components/CardNameDetail'
import CardDetail from '@/components/CardDetail'
import Home from '@/components/Home'

Vue.use(Router)

export default new Router({
    routes: [
        {
            path: '/',
            name: 'Home',
            component: Home
        },
        {
            path: '/tournaments/',
            name: 'Tournaments',
            component: Tournaments
        },
        {
            path: '/tournaments/:tournamentId',
            name: 'TournamentDetail',
            component: TournamentDetail
        },
        {
            path: '/decks/:deckId',
            name: 'DeckDetail',
            component: DeckDetail
        },
        {
            path: '/cards/:cardName',
            name: 'CardNameDetail',
            component: CardNameDetail
        },
        {
            path: '/card/:cardId',
            name: 'CardDetail',
            component: CardDetail
        },
    ]
})
