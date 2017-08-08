"""
@author: Thomas PERROT

Contains tasks for stats app
"""


from typing import Dict
from datetime import date, timedelta
import numbers
import re

from celery import shared_task
from celery.utils.log import get_task_logger
import requests
from bs4 import BeautifulSoup
from celery.exceptions import SoftTimeLimitExceeded
from django.utils import timezone

from . import utils
from .models import Features, Statistics, Price
from cards.models import Card
from tournaments.models import Tournament


logger = get_task_logger(__name__)


MKM_URL = 'http://www.magiccardmarket.eu/'
MKM_BASE_CARD_URL = 'http://www.magiccardmarket.eu/Products/Singles/{set}/{card_name}'

MAX_PAGES = 30
DATE = re.compile(r"\w{1,10} \d{1,2}, \d{4}")


def parse_page(content: str) -> Dict[str, numbers.Real]:
    """Parses the given single product page.

    Returns the number of available items, the lowest price, the mean price, and the lowest price and available items
    for foil (if exist).

    Page HTML structure depends on whether foil version of the card exists. Mean price tag will changes.
    """

    soup = BeautifulSoup(content, 'html.parser')

    sells_table = soup.find("table", {"class": "availTable"})

    parsed_response = {}

    available_items = sells_table.find("span", {"itemprop": "offerCount"}).get_text()  # e.g 1001
    parsed_response['available_items'] = int(available_items)

    try:
        min_price = sells_table.find("span", {"itemprop": "lowPrice"}).get_text()  # e.g "0,02"
    except AttributeError:
        pass
    else:
        try:
            # Sometime min price is 'N/A'
            parsed_response['min_price'] = float(min_price.replace(',', '.'))
        except ValueError:
            pass

    # Parses mean price which depends on the page HTML structure...
    try:
        mean_price = sells_table.find("td", {
            "class": "outerRight col_Odd col_1 cell_2_1"}).get_text()  # e.g 0,15 €
    except AttributeError:
        try:
            mean_price = sells_table.find("td", {
                "class": "outerBottom outerRight col_Odd col_1 cell_2_1"}).get_text()  # e.g 0,15 €
        except AttributeError:
            pass
        else:
            parsed_response['mean_price'] = float(mean_price.strip(' €').replace(',', '.'))
    else:
        parsed_response['mean_price'] = float(mean_price.strip(' €').replace(',', '.'))

    try:
        available_foils = sells_table.find("td", {
            "class": "outerRight col_Odd col_1 cell_3_1"}).get_text()  # e.g 101
        min_foil_price = sells_table.find("td", {
            "class": "outerBottom outerRight col_Odd col_1 cell_4_1"}).get_text()  # e.g 0,15 €
    except AttributeError:
        # Foil version does not exist for this card
        pass
    else:
        try:
            # Sometime min price is 'N/A'
            parsed_response['min_foil'] = float(min_foil_price.strip(' €').replace(',', '.'))
        except ValueError:
            pass
        parsed_response['available_foils'] = int(available_foils)

    return parsed_response


@shared_task(soft_time_limit=10,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Get card price',
             ignore_result=True,
             rate_limit='10/m')
def get_price(card_id: str) -> None:
    """Gets the prices and quantity for the given card and stores them in database.
    """

    card = Card.objects.get(id=card_id)
    logger.info('Getting price of card {} for set {}. Url: {}'.format(card.name, card.set, card.mkm_url))

    url = card.mkm_url
    if not url:
        return

    r = requests.get(url)
    if 'The requested article does not exist.' in r.text:
        if card.layout == 'double-faced':
            logger.warning('Unknown url for MKM: {} (double-faced card)'.format(url))
        else:
            logger.exception('Unknown url for MKM: {}'.format(url))
        return

    parsed_prices = parse_page(r.text)

    card = Card.objects.get(id=card_id)
    price, created = Price.objects.get_or_create(card=card, date=timezone.now(), defaults=parsed_prices)

    if created:
        logger.debug('Inserted price {}'.format(price))


@shared_task(name='Get relevant cards price',
             ignore_result=True)
def harvest_prices() -> None:
    """Harvests all prices for relevant cards.
    """

    relevant_cards = Card.objects.filter(is_relevant=True)

    for card in relevant_cards:
        if Price.objects.filter(card=card, date=timezone.now()).exists():
            logger.debug('Price already exists for card {}'.format(card))
        else:
            get_price.delay(card.id)


@shared_task(name='Compute statistics')
def compute_statistics() -> None:
    """Compute all the statistics for every relevant cards.

    This step needs to be done after all steps have finished.
    """

    logger.info('Computing cards statistics')

    class Classifier:
        # TODO: implement me :'(
        @staticmethod
        def predict(_):
            return 0

    for card in Card.objects.filter(is_relevant=True):

        logger.debug('Predicting price for card {}...'.format(card))
        features = Features.objects.get(card=card, date=date.today())
        predicted_price = Classifier.predict(features.features)

        logger.debug('Computing price ratio for card {}...'.format(card))
        current_prices = Price.objects.get(card=card, date=date.today())
        price_ratio = predicted_price / current_prices.mean_price

        logger.debug('Computing playing ratio for card {}...'.format(card))
        played_cards = Tournament.get_played_cards(date.today(),
                                                   date.today() - timedelta(days=Statistics.PLAYING_WINDOW))
        playing_ratio = played_cards[card.name.name] / sum(played_cards.values())

        statistics, created = Statistics.objects.get_or_create(card=card, date=date.today(), defaults={
            'predicted_price': predicted_price, 'price_ratio': price_ratio, 'playing_ratio': playing_ratio})
        if created:
            logger.debug('Created statistics {}'.format(statistics))


@shared_task(name='Compute all features',
             ignore_result=True)
def compute_features() -> None:
    """Computes all features for card that have been played in tournaments for last two weeks.
    """

    for card_id, usages in utils.usage_feature(0):

        card = Card.objects.get(id=card_id)

        if not card.is_relevant:
            logger.debug('Card {} is irrelevant for features computing. Skipping.'.format(card))
            continue

        if Features.objects.filter(card=card, date=date.today()).exists():
            logger.debug('Features already exist for card {} on date {}'.format(card, date.today()))
            continue

        logger.info('Computing feature for card {}'.format(card))

        try:
            features = {
                'usages': usages,
                'prices': utils.price_feature(card_id, 0),
                'price_differences': utils.price_difference_feature(card_id, 0),
                'sales_volume': utils.sales_volume_feature(card_id, 0),
                'mana_cost': utils.mana_cost_feature(card_id),
                'tournament_legality': utils.tournament_legality_feature(card_id),
                'price_variance': utils.price_variance_feature(card_id, 0),
                'labels': utils.get_labels(card_id, 0)
            }
        except Exception as err:
            logger.exception('Could not compute features for card {}: {}'.format(card, err))
        else:
            Features.objects.create(card=card, date=date.today(), features=features)
            logger.debug('Computed features for card {}'.format(card.name))
