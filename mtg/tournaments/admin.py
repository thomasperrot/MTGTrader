"""
@author: Thomas PERROT

Contains admin settings for tournaments app
"""


from django.contrib import admin

from .models import Tournament, Deck, DeckPosition, DeckToCard


class DeckPositionInline(admin.TabularInline):
    model = DeckPosition
    ordering = ('position',)
    extra = 1
    raw_id_fields = ('deck', 'tournament')


class DeckToCardInline(admin.TabularInline):
    model = DeckToCard
    ordering = ('sideboard',)
    classes = ['collapse']
    extra = 1
    raw_id_fields = ('card_name', 'deck')


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    inlines = (DeckPositionInline,)
    search_fields = ('id', 'name', 'event_date', 'format__name',)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    inlines = (DeckPositionInline, DeckToCardInline,)
    search_fields = ('id', 'name', 'owner', 'cards__name',)


admin.site.register(DeckPosition)
admin.site.register(DeckToCard)
