"""
@author: Thomas PERROT

Contains admin settings for cards app
"""


from datetime import date

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from stats.admin import PriceInline

from .models import Card, CardName


class CardInline(admin.TabularInline):
    model = Card
    fields = ('rarity', 'set', 'artist', 'layout')
    extra = 1

    class Meta:
        verbose_name = 'printings'
        verbose_name_plural = 'printings'


class MkmListFilter(admin.SimpleListFilter):
    title = _('MKM crawling results')

    parameter_name = 'mkm-crawling'

    def lookups(self, request, model_admin):
        return (
            ('succeeded', _('succeeded to crawl')),
            ('failed_today', _('failed to crawl today')),
            ('failed_always', _('failed to crawl always')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'succeeded':
            return queryset.filter(
                is_relevant=True,
                prices__isnull=False
            ).distinct()

        if self.value() == 'failed_today':
            return queryset.filter(
                is_relevant=True,
            ).exclude(
                prices__date__lte=date.today()
            ).distinct()

        if self.value() == 'failed_always':
            return queryset.filter(
                is_relevant=True,
                prices__isnull=True
            ).distinct()


class FeaturesListFilter(admin.SimpleListFilter):
    title = _('Features computing results')

    parameter_name = 'features-computing'

    def lookups(self, request, model_admin):
        return (
            ('succeeded', _('succeeded to compute')),
            ('failed_today', _('failed to compute today')),
            ('failed_always', _('failed to compute always')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'succeeded':
            return queryset.filter(
                is_relevant=True,
                features__isnull=False
            ).distinct()

        if self.value() == 'failed_today':
            return queryset.filter(
                is_relevant=True,
            ).exclude(
                features__date__lte=date.today()
            ).distinct()

        if self.value() == 'failed_always':
            return queryset.filter(
                is_relevant=True,
                features__isnull=True
            ).distinct()


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name__name')
    actions = ('set_relevant', 'set_irrelevant')
    list_filter = ('is_relevant', MkmListFilter, FeaturesListFilter)
    inlines = (PriceInline,)
    raw_id_fields = ('name', 'set', 'printings', 'names')

    def set_relevant(self, request, queryset):
        rows_updated = queryset.update(is_relevant=True)
        if rows_updated == 1:
            message = "1 card was"
        else:
            message = "{} cards were".format(rows_updated)
        self.message_user(request, "{} successfully set as relevant.".format(message))

    def set_irrelevant(self, request, queryset):
        rows_updated = queryset.update(is_relevant=False)
        if rows_updated == 1:
            message = "1 card was"
        else:
            message = "{} cards were".format(rows_updated)
        self.message_user(request, "{} successfully set as irrelevant.".format(message))


@admin.register(CardName)
class CardNameAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    inlines = [CardInline]
