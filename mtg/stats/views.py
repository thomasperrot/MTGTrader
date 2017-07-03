"""
@author: Thomas PERROT

Contains views for stats app
"""


from datetime import date

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from . import serializers
from . import tasks
from .models import Price, Statistics


class PriceViewSet(viewsets.ReadOnlyModelViewSet):
    """A view that allow the user to get data on prices that have been crawled.
    """

    queryset = Price.objects.all()
    serializer_class = serializers.PriceSerializer


class StatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """A view that allow the user to get data on prices predictions.
    """

    queryset = Statistics.objects.all()
    serializer_class = serializers.StatisticsSerializer

    @list_route()
    def get_highest_increment(self, request) -> Response:
        """Returns the cards that are expected to have the highest price increment in the future.
        """

        cards = []
        highest_predictions = Statistics.objects.filter(date=date.today()).order_by('-price_ratio')[:50]
        for prediction in highest_predictions:
            cards.append(prediction.card)

        serializer = self.get_serializer(cards, many=True)
        return Response(serializer.data)

    @list_route()
    def get_highest_decrement(self, request) -> Response:
        """Returns the cards that are expected to have the highest price decrement in the future.
        """

        cards = []
        highest_predictions = Statistics.objects.filter(date=date.today()).order_by('price_ratio')[:50]
        for prediction in highest_predictions:
            cards.append(prediction.card)

        serializer = self.get_serializer(cards, many=True)
        return Response(serializer.data)


def harvest_prices(request):
    """Temporary view to get all cards prices.
    """

    # TODO: remove me

    tasks.harvest_prices.delay()
    return HttpResponse("<html><body>Harvesting prices...</body></html>")


def compute_features(request):
    """Temporary view to compute all features.
    """

    # TODO: remove me

    tasks.compute_features.delay()
    return HttpResponse("<html><body>Computing features...</body></html>")
