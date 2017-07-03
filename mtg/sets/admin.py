"""
@author: Thomas PERROT

Contains admin settings for sets app
"""


from django.contrib import admin

from .models import Set, Booster, Slot


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 1


@admin.register(Booster)
class BoosterAdmin(admin.ModelAdmin):
    inlines = (SlotInline,)
    search_fields = ('set__name',)


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    search_fields = ('id', 'name',)
    actions = ['set_relevant', 'set_irrelevant']
    list_filter = ('is_relevant',)

    def set_relevant(self, request, queryset):
        rows_updated = queryset.update(is_relevant=True)
        if rows_updated == 1:
            message = "1 set was"
        else:
            message = "{} sets were".format(rows_updated)
        self.message_user(request, "{} successfully set as relevant.".format(message))

    def set_irrelevant(self, request, queryset):
        rows_updated = queryset.update(is_relevant=False)
        if rows_updated == 1:
            message = "1 set was"
        else:
            message = "{} sets were".format(rows_updated)
        self.message_user(request, "{} successfully set as irrelevant.".format(message))
