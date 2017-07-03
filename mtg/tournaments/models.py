"""
@author: Thomas PERROT

Contains models for tournaments app
"""


from typing import Dict
from collections import defaultdict
from datetime import date

from django.db import models

from cards.models import Card, CardName


class Format(models.Model):
    """Class which represents a format (e.g Legacy, Modern, etc.).
    """

    FORMATS = (
        ('commander', 'Commander'),
        ('legacy', 'Legacy'),
        ('modern', 'Modern'),
        ('vintage', 'Vintage'),
        ('standard', 'Standard')
    )

    name = models.CharField(max_length=100, primary_key=True, choices=FORMATS)
    legalities = models.ManyToManyField(
        Card,
        through='Legality',
        blank=True
    )

    def __str__(self) -> str:
        return self.name.capitalize()


class Deck(models.Model):
    """Class which represents a deck.
    """

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, blank=True)
    owner = models.CharField(max_length=50, blank=True)
    cards = models.ManyToManyField(CardName, through='DeckToCard')

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.owner)


class Tournament(models.Model):
    """Class which represents a tournament.
    """

    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    event_date = models.DateField()
    format = models.ForeignKey(Format)
    results = models.ManyToManyField(Deck, through='DeckPosition')

    def __str__(self) -> str:
        return '{}  {}  {}'.format(self.format, self.event_date.strftime('%d/%m/%y'), self.name)

    class Meta:
        ordering = ['-event_date']

    @classmethod
    def get_played_cards(cls, to_date: date=None, from_date: date=None) -> Dict[str, int]:
        """Gets all cards that have been played in tournaments between date_1 and date_2.
        Returns a dictionary mapping CardName id with the number of times it has been played.
        """

        kwargs = {}
        if to_date:
            kwargs['event_date__lte'] = to_date
        if from_date:
            kwargs['event_date__gte'] = from_date
        tournaments = cls.objects.filter(**kwargs)

        played_cards = defaultdict(int)

        for tournament in tournaments:
            for deck in tournament.results.all():
                for deck_to_card in DeckToCard.objects.filter(deck=deck):
                    played_cards[deck_to_card.card_name.name] += deck_to_card.number

        return played_cards


class DeckToCard(models.Model):
    """Class which represents the relation between a deck and its cards.
    """

    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card_name = models.ForeignKey(CardName, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField()
    sideboard = models.BooleanField(blank=True, default=False)

    def __str__(self) -> str:
        return '{} <-> {} ({})'.format(self.deck, self.card_name, self.number)

    class Meta:
        unique_together = ("deck", "card_name", "sideboard")


class Legality(models.Model):
    """Class which represents the legality of a given card in a given format.
    """

    LEGALITY = (
        ('legal', 'Legal'),
        ('banned', 'Banned'),
        ('restricted', 'Restricted')
    )

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    format = models.ForeignKey(Format, on_delete=models.CASCADE)
    legality = models.CharField(max_length=20, choices=LEGALITY)


class DeckPosition(models.Model):
    """Class which links a tournament and the results, which are the positions of the decks.
    """

    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        return '{} <-> {} ({})'.format(self.deck, self.tournament, self.position)

    class Meta:
        unique_together = ("deck", "tournament")
