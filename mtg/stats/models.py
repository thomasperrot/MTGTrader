"""
@author: Thomas PERROT

Contains models for stats app
"""


from django.contrib.postgres.fields import JSONField
from django.db import models

from cards.models import Card


class Price(models.Model):
    """Class which represents the price(s) of a given card at a given time.
    """

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='prices')
    date = models.DateField()
    available_items = models.SmallIntegerField()
    min_price = models.FloatField(blank=True, null=True)
    mean_price = models.FloatField(blank=True, null=True)
    available_foils = models.SmallIntegerField(blank=True, null=True)
    min_foil = models.FloatField(blank=True, null=True)

    def __str__(self) -> str:
        return '{} ({})'.format(self.card, self.date.strftime('%d/%m/%y'))

    class Meta:
        unique_together = ("card", "date")
        get_latest_by = "date"


class Features(models.Model):
    """Class which stores features for a given card on a given day.
    """

    card = models.ForeignKey(Card)
    date = models.DateField(auto_now=True)
    features = JSONField()

    def __str__(self) -> str:
        return '{} ({})'.format(self.card, self.date)

    class Meta:
        unique_together = ("card", "date")
        verbose_name_plural = "Features"


class Statistics(models.Model):
    """Class which stores some heavy computing statistics for a given card on a given day. It allows to efficiently
    get cards statistics without computing it for every request, but computing it in the background once for all.

    Statistics are:
        - prediction: the price predicted by the classifier
        - price_ratio: the ratio between the predicted price and the current price
        - playing_ratio: the playing ratio for the given card. Tournaments are discreet and random events,
            so one single day can not be representative. We have to aggregate on tournaments over a certain period
            to avoid random results. The chosen period is 3 days.
    """

    PLAYING_WINDOW = 3

    card = models.ForeignKey(Card, related_name='stats')
    date = models.DateField(auto_now=True)
    predicted_price = models.FloatField()
    price_ratio = models.FloatField()
    playing_ratio = models.FloatField()

    def __str__(self) -> str:
        return '{} ({})'.format(self.card.name, self.date)

    class Meta:
        unique_together = ("card", "date")
        verbose_name_plural = "Statistics"
