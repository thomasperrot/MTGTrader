"""
@author: Thomas PERROT

Contains serializers for stats app
"""


from rest_framework import serializers

from .models import Price, Statistics


class PriceSerializer(serializers.HyperlinkedModelSerializer):
    card_id = serializers.ReadOnlyField(source='card.id')

    class Meta:
        model = Price
        fields = ('card_id', 'date', 'available_items', 'min_price', 'mean_price', 'available_foils', 'min_foil')


class StatisticsSerializer(serializers.HyperlinkedModelSerializer):
    card_id = serializers.ReadOnlyField(source='card.id')
    card_name = serializers.ReadOnlyField(source='card.name.name')
    card_set = serializers.ReadOnlyField(source='card.set.name')

    class Meta:
        model = Statistics
        fields = ('card_id', 'card_name', 'card_set', 'date', 'predicted_price', 'price_ratio', 'playing_ratio')
