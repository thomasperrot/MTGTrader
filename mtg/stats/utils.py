"""
@author: Thomas PERROT

Contains some utils for stats app
"""


from typing import Dict, Iterator, Tuple, List
from datetime import date, timedelta
from statistics import variance, mean
from collections import defaultdict

from .models import Price
from sets.models import Set
from cards.models import Card
from tournaments.models import Tournament


def price_feature(card_id: str, d: int) -> List[float]:
    """Returns the mean prices of the card for day d and preceding week (features 1-7).
    """

    prices = Price.objects.filter(
        card__id=card_id,
        date__lte=date.today() - timedelta(days=d),
        date__gte=date.today() - timedelta(days=d + 6)
    ).order_by('-date')
    return [p.mean_price for p in prices]


def price_difference_feature(card_id: str, d: int) -> List[float]:
    """Returns the price differences between day d and each of the previous 6 days (features 8-13).
    """

    prices = price_feature(card_id, d)
    if len(prices) <= 1:
        return prices

    prices_difference = [prices[0] - p for p in prices[1:]]
    return prices_difference


def usage_feature(d: int) -> Iterator[Tuple[str, List[float]]]:
    """Computes usage difference between day d and each of the previous 6 days (features 14-19).

    Usage is defined as the ratio between the number of times it appears in every deck and the total of cards
    that appears in every deck.

    Simple stats: only about 1000 different cards are played in tournaments
    """

    card_id_to_usages = defaultdict(list)

    # Gets all cards that have been played for two weeks.
    all_cards = set(Tournament.get_played_cards(
        date.today() - timedelta(days=d),
        date.today() - timedelta(days=d + 13)
    ))

    for i in range(7):

        played_cards = Tournament.get_played_cards(
            date.today() - timedelta(days=d + i),
            date.today() - timedelta(days=d + i + 6)
        )
        total = sum(played_cards.values())

        for card_name in all_cards:
            usage = played_cards.get(card_name, 0) / total
            for card in Card.objects.filter(name=card_name):
                card_id_to_usages[card.id].append(usage)

    for card_id, usages in card_id_to_usages.items():
        if len(usages) > 1:
            yield card_id, [usages[0] - usage for usage in usages[1:]]
        else:
            yield card_id, usages


def sales_volume_feature(card_id: str, d: int) -> List[int]:
    """Returns sales volume difference between day d and each of the previous 6 days. (features 20-25).
    """

    prices = Price.objects.filter(
        card__id=card_id,
        date__lte=date.today() - timedelta(days=d),
        date__gte=date.today() - timedelta(days=d + 6)
    ).order_by('-date')

    if len(prices) <= 1:
        return [p.available_items for p in prices]
    return [prices[0].available_items - price.available_items for price in prices[1:]]


def mana_cost_feature(card_id: str) -> int:
    """Returns the converted mana cost of the card (feature 26).
    """

    return Card.objects.get(id=card_id).cmc


def tournament_legality_feature(card_id: str) -> int:
    """Returns the number of days until card loses tournament legality in standard format (feature 27).
    Returns -1 if card is already banned in standard.

    Their are 2 sets every year, and only the last 3 sets are legal at the same time in standard format.
    To be exact, it is 575 days: Battle for Zendikar release date as October 2, 2015 and became illegal
    for Amonkhet release on April 28, 2017.
    """

    t2_rotation = 575
    legal_types = ('core', 'expansion')

    card_name = Card.objects.get(id=card_id).name

    cards = Card.objects.filter(name=card_name)
    sets = Set.objects.filter(id__in=[card.set.id for card in cards])

    dates = [s.release_date for s in sets if s.type in legal_types]

    if dates:
        most_recent = max(dates)
        day_before_exp = most_recent + timedelta(t2_rotation) - date.today()
        return day_before_exp.days if day_before_exp.days >= 0 else -1

    return -1


def price_variance_feature(card_id: str, d: int) -> float:
    """Returns the variance of past week’s prices (feature 28)."""

    prices = price_feature(card_id, d)
    if len(prices) <= 1:
        return prices

    return variance(prices)


def get_labels(card_id: str, d: int) -> Dict[int, bool]:
    """Returns the labels.
        - label_1: True if price on day d is less than average price over following week,
        - label_2: True if price on day D is less than minimum price over following week,
        - label_3: True if price on day D is at least $0.50 less than average price over following week,
        - label_4: True if price on day D is at least $0.50 less than minimum price over following week
    """

    prices = price_feature(card_id, d)

    if len(prices) <= 1:
        return {i: False for i in range(1, 5)}

    return {
        1: prices[0] < mean(prices[1:]),
        2: prices[0] < min(prices[1:]),
        3: prices[0] < mean(prices[1:]) - 0.5,
        4: prices[0] < min(prices[1:]) - 0.5
    }
