"""
@author: Thomas PERROT

Contains views for cards app
"""


from datetime import date, timedelta

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from . import serializers
from .models import CardName, Card
import stats
import tournaments


class CardNameViewSet(viewsets.ReadOnlyModelViewSet):
    """View for card names.
    """

    queryset = CardName.objects.order_by('name')
    serializer_class = serializers.CardNameSerializer
    search_fields = ('name',)


class CardViewSet(viewsets.ReadOnlyModelViewSet):
    """View for cards.
    """

    queryset = Card.objects.order_by('name')
    serializer_class = serializers.CardSerializer
    search_fields = ('name', 'set')

    @list_route()
    def get_failed_mkm(self, request) -> Response:
        """Returns cards that have failed being crawled on magiccardmarket.eu.
        """

        failed_cards = Card.objects.filter(
            is_relevant=True,
            price__isnull=True
        ).exclude(
            layout='double-faced'
        )

        serializer = self.get_serializer(failed_cards, many=True)
        return Response(serializer.data)

    @detail_route()
    def get_prices(self, request, pk=None) -> Response:
        """Returns last month prices for the given card.
        """

        card = get_object_or_404(Card, id=pk)
        prices = card.prices.filter(date__gte=date.today() - timedelta(days=30))

        serializer = stats.serializers.PriceSerializer(prices, many=True)
        return Response(serializer.data)

    @detail_route()
    def get_playing_ratio(self, request, pk=None) -> Response:
        """Returns last month playing ratio for the given card.

        Tournaments are discreet and random events, so one single day can not be representative. We have
        to aggregate on tournaments over a certain period to avoid random results. The chosen period is 3 days.
        """
        # TODO: This is to slow ! we need to compute it in the background !

        card = get_object_or_404(Card, id=pk)
        card_name = card.name.name

        days_in_month = 30
        aggregating_period = 3

        playing_ratio = []

        for i in range(0, days_in_month // aggregating_period, aggregating_period):
            played_cards = tournaments.models.Tournament.get_played_cards(
                date.today() - timedelta(days=i), date.today() - timedelta(days=i + aggregating_period))
            playing_ratio.append({'date': date.today() - timedelta(days=i),
                                  'ratio': played_cards[card_name] / sum(played_cards.values())})

        return Response(playing_ratio)

    @detail_route()
    def get_statistics(self, request, pk=None) -> Response:
        """Returns all the statistics for the given card for ast month.
        """

        card = get_object_or_404(Card, id=pk)
        stats = card.stats.filter(date__gte=date.today() - timedelta(30))

        serializer = stats.serializers.StatisticsSerializer(stats, many=True)
        return Response(serializer.data)

    @detail_route()
    def get_features(self, request, pk=None) -> Response:
        """Returns today features for the given cards.
        """

        card = get_object_or_404(Card, id=pk)
        features = card.features_set.filter(date=date.today())

        return Response(features.features)
