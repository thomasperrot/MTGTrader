"""
@author: Thomas PERROT

Contains admin settings for stats app
"""


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Price, Statistics, Features


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-date')


class HasMeanPrice(admin.SimpleListFilter):
    title = _('Are data valid')

    parameter_name = 'has-mean-price'

    def lookups(self, request, model_admin):
        return (
            ('has_mean', _('has mean price')),
            ('has_no_mean', _('has no mean price')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'has_mean':
            return queryset.filter(
                mean_price__isnull=False,
            )

        if self.value() == 'has_no_mean':
            return queryset.filter(
                mean_price__isnull=True,
            )


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    exclude = ('card',)
    search_fields = ('date',)
    list_filter = (HasMeanPrice,)


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    exclude = ('card',)
    search_fields = ('date',)


@admin.register(Features)
class FeaturesAdmin(admin.ModelAdmin):
    exclude = ('card',)
    search_fields = ('date',)
