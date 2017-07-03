"""
@author: Thomas PERROT

Contains serializers for cards app
"""


from rest_framework import serializers

from .models import CardName, Card


class CardTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('types',)


class PrintingSerializer(serializers.ModelSerializer):
    set_name = serializers.ReadOnlyField(source='set.name')
    set_id = serializers.ReadOnlyField(source='set.id')

    class Meta:
        model = Card
        fields = ('id', 'set_name', 'set_id')


class CardNameSerializer(serializers.ModelSerializer):
    printings = PrintingSerializer(source='card_set', many=True)

    class Meta:
        model = CardName
        fields = ('name', 'printings')


class CardSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='name.name')
    set = serializers.ReadOnlyField(source='set.name')

    class Meta:
        model = Card
        fields = ('id', 'name', 'set')
        # fields = (
        #     'id', 'name', 'rarity', 'set', 'printings', 'artist', 'layout', 'slug', 'power', 'toughness',
        #     'loyalty', 'names', 'mana_cost', 'cmc', 'colors', 'colors_identity', 'types', 'sub_types', 'super_types',
        #     'text', 'flavor', 'border', 'multiverse_id', 'image_url', 'original_text', 'original_type', 'legalities',
        #     'number', 'source', 'timeshifted', 'hand', 'life', 'release_date', 'starter', 'variations'
        # )
