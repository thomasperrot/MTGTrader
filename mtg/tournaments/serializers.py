"""
@author: Thomas PERROT

Contains serializers for tournaments app
"""


from typing import Dict
from operator import itemgetter

from rest_framework import serializers

from .models import Tournament, Deck, DeckPosition, DeckToCard
from cards.serializers import CardTypeSerializer


class DeckToCardSerializer(serializers.ModelSerializer):
    card_name = serializers.ReadOnlyField(source='card_name.name')
    card_type = CardTypeSerializer(source='card_name.card_set', many=True, read_only=True)

    class Meta:
        model = DeckToCard
        fields = ('card_name', 'card_type', 'number', 'sideboard')


class DeckDetailSerializer(serializers.ModelSerializer):
    """Returns the detail content of a deck (with cards).
    """

    cards = DeckToCardSerializer(source='decktocard_set', many=True, read_only=True)

    class Meta:
        model = Deck
        fields = ('id', 'name', 'owner', 'cards')

    def to_representation(self, instance) -> Dict:
        """Converts the deck to a correct representation for API.

        A conversion needs to be done with "card_type" attribute, which has the following shape at first.
        [
            OrderedDict([('types', ['land'])]),
            OrderedDict([('types', ['land'])]),
            ...
        ]
        """

        data = super().to_representation(instance)
        cards = data.pop('cards')

        main_deck, sideboard = [], []
        for card in cards:

            card_types = set()
            for types in card.pop('card_type'):
                card_types |= {k for v in types.values() for k in v}
            card['types'] = list(card_types)

            in_sideboard = card.pop('sideboard')
            if in_sideboard:
                sideboard.append(card)
            else:
                main_deck.append(card)

        data['cards'] = {
            'main_deck': main_deck,
            'sideboard': sideboard
        }

        return data


class DeckListSerializer(serializers.ModelSerializer):
    """Returns the list of all decks.
    """

    class Meta:
        model = Deck
        fields = ('id', 'name', 'owner')


class DeckPositionSerializer(serializers.ModelSerializer):
    deck_id = serializers.ReadOnlyField(source='deck.id')
    deck_name = serializers.ReadOnlyField(source='deck.name')
    deck_owner = serializers.ReadOnlyField(source='deck.owner')

    class Meta:
        model = DeckPosition
        fields = ('deck_id', 'deck_name', 'deck_owner', 'position')


class TournamentSerializer(serializers.ModelSerializer):
    decks = DeckPositionSerializer(source='deckposition_set', many=True)
    format_name = serializers.ReadOnlyField(source='format.name')

    class Meta:
        model = Tournament
        fields = ('id', 'name', 'event_date', 'format_name', 'decks')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['decks'] = sorted(data['decks'], key=itemgetter('position'))
        return data
