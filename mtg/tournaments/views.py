"""
@author: Thomas PERROT

Contains views for tournaments app
"""


from django.http import HttpResponse
from rest_framework import viewsets

from . import serializers
from . import tasks
from .models import Tournament, Deck


class TournamentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows tournaments to be viewed.
    Tournaments can either be viewed as list (without decks list), or detailed (with decks list)
    """

    queryset = Tournament.objects.order_by('-event_date')
    search_fields = ('name', 'format_name')
    ordering_fields = ('event_date', 'format_name')
    serializer_class = serializers.TournamentSerializer


class DeckViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows decks to be viewed.
    Decks can either be viewed as list (without cards list), or detailed (with cards list)
    """

    queryset = Deck.objects.all()
    search_fields = ('name', 'owner')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.DeckListSerializer
        if self.action == 'retrieve':
            return serializers.DeckDetailSerializer


def harvest_formats(request):
    """Temporary view to harvest last tournaments.
    """

    # TODO: remove me

    tasks.harvest_formats.delay(force=True)
    return HttpResponse("<html><body>Harvesting last tournaments...</body></html>")


def get_deck(request, deck_id):
    """Temporary view to harvest a single deck.
    """

    # TODO: remove me

    tasks.get_deck.delay(deck_id)
    return HttpResponse("<html><body>Harvesting deck {}...</body></html>".format(deck_id))


def update_relevance(request):
    """Temporary view to update all cards relevance.
    """

    # TODO: remove me

    tasks.update_relevance.delay()
    return HttpResponse("<html><body>Updating relevance...</body></html>")

