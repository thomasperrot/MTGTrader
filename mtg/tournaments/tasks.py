"""
@author: Thomas PERROT

Contains tasks for tournaments app
"""


from typing import Generator
import re
from datetime import datetime, date, timedelta

import requests
import bs4.element
from bs4 import BeautifulSoup
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task, group
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from .models import Tournament, Deck, Format, DeckToCard, DeckPosition
from cards.models import CardName, Card


logger = get_task_logger(__name__)

MTG_TOP8_URL = 'http://mtgtop8.com/'
MTGO_URL = 'http://mtgtop8.com/mtgo?d={}'

TOURNAMENT_URL_REGEX = re.compile(r'event\?e=(?P<tournament_id>\d{1,5})&f=(?P<format_id>[A-Z]{2})')
DECK_URL_REGEX = re.compile(r'\?e=(?P<tournament_id>\d{1,5})&d=(?P<deck_id>\d{1,6})&f=(?P<format_id>[A-Z]{2})')
MTGO_CARD_LINE_REGEX = re.compile(r'(?P<number>\d) (?P<name>.{1,100})')

FORMATS = {
    'VI': 'vintage',
    'LE': 'legacy',
    'MO': 'modern',
    'ST': 'standard',
    'EDH': 'commander'
}


@shared_task(name='Update relevance')
def update_relevance() -> None:
    """Updates relevance of cards in database.

    All rare and mythic cards that has been played in last two weeks tournaments, and whose set
    is relevant (i.e is not only online) are considered as relevant.
    """

    logger.info('Updating cards relevance in database...')

    Card.objects.update(is_relevant=False)

    for card_name in Tournament.get_played_cards(date.today(), date.today() - timedelta(days=14)):
        Card.objects.filter(
            name__name=card_name,
            rarity__rarity__in=('R', 'M'),
            set__is_relevant=True
        ).update(
            is_relevant=True
        )

    logger.info('Relevant cards: {}'.format(Card.objects.filter(is_relevant=True).count()))


def parse_mtgo_deck(content: str) -> Generator:
    """Parses the content of a mtgo export.
    """

    sideboard = False

    for line in content.split('\n'):
        match = MTGO_CARD_LINE_REGEX.match(line)
        if match:
            # Handles cards such as "Fire/Ice"
            if '/' in match.group('name'):
                card_names = [name_part.strip() for name_part in match.group('name').split('/')]
            else:
                card_names = [match.group('name').strip()]
            for name in card_names:
                yield {
                    'name': name,
                    'number': int(match.group('number')),
                    'sideboard': sideboard
                }
        elif line.strip() == 'Sideboard':
            sideboard = True


def parse_tournaments(soup: bs4.BeautifulSoup) -> Generator:
    """Parses the soup element representing the last 10 tournaments for a format.
    Yields data about each tournament.
    """

    for tournament_tag in soup.find("tr", text="Last 10 events").next_siblings:
        if tournament_tag.find("td") != -1:

            a_tag = tournament_tag.find("a")
            href = tournament_tag.find("a")['href']
            tournament = {
                'name': a_tag.text,
                'url': MTG_TOP8_URL + href,
                'id': TOURNAMENT_URL_REGEX.match(href).group('tournament_id')
            }
            t_date = tournament_tag.find("td", {"class": "S10"}).text
            tournament['date'] = timezone.make_aware(
                datetime.strptime(t_date, '%d/%m/%y'), timezone.get_current_timezone())

            yield tournament


def parse_decks(soup: bs4.BeautifulSoup) -> Generator:
    """Parses the soup element representing the detail of a tournament, with the winning decks.
    Yields data about each deck.
    """

    players_link = soup.find_all("div", {"class": "G11"})
    decks = [link.parent for link in players_link]

    for deck_tag in decks:

        tags = list(deck_tag.children)[1::2]  # Removed "\n" elements

        position = tags[0].text
        if '-' in position:
            position = position.split('-')[1]
        try:
            position = int(position)
        except ValueError:
            logger.exception('Could not convert deck position to integer: {}'.format(position))
            continue

        deck = {
            'position': position,
            'link': tags[1].a['href'],
            'deck_name': tags[1].text,
            'player': tags[2].text
        }
        deck.update(DECK_URL_REGEX.match(deck['link']).groupdict())

        yield deck


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Harvest deck',
             ignore_result=True,
             rate_limit='10/m')
def get_deck(deck_id: str) -> None:
    """Gets the deck cards from the given id.

    Fetches the .mwDeck page, parses it, and creates DeckToCards.
    """

    logger.info('Extracting data from deck {}...'.format(deck_id))

    export_deck_url = MTGO_URL.format(deck_id)

    r = requests.get(export_deck_url)

    logger.debug('Instantiating Django objects...')
    deck = Deck.objects.get(id=deck_id)

    for card_dict in parse_mtgo_deck(r.text):
        try:
            card_name_obj = CardName.objects.get(name=card_dict['name'])
        except ObjectDoesNotExist:
            logger.error('Unknown card name: {}'.format(card_dict['name']))
        else:

            deck_to_card, created = DeckToCard.objects.get_or_create(
                deck=deck,
                card_name=card_name_obj,
                sideboard=card_dict['sideboard'],
                defaults={'number': card_dict['number']}
            )
            if created:
                logger.debug('Successfully inserted DeckToCard {}'.format(deck_to_card))


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Harvest tournament',
             ignore_result=True,
             rate_limit='10/m')
def get_tournament(url: str) -> None:
    """Get all Decks objects from the given tournament url.

    Parses and instantiates all decks that appear in the tournament detail page. If a position of the deck is created
    (i.e the deck is unknown for that tournament), we crawl the deck detail and store it in database.
    The tournament url must have the following shape: http://mtgtop8.com/event?e=15191&f=MO
    """

    logger.info('Extracting data for tournament {}'.format(url))

    logger.debug('Fetching tournament page {}...'.format(url))
    r = requests.get(url)

    logger.debug('Parsing tournament {}...'.format(url))
    soup = BeautifulSoup(r.text, 'html.parser')

    for deck in parse_decks(soup):

        deck_obj = Deck(id=deck['deck_id'], name=deck['deck_name'], owner=deck['player'])
        deck_obj.save()

        tournament = Tournament.objects.get(id=deck['tournament_id'])
        deck_position, created = DeckPosition.objects.get_or_create(
            deck=deck_obj, tournament=tournament, defaults={'position': deck['position']})

        if created:
            get_deck.delay(deck['deck_id'])


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Harvest all tournaments in format',
             ignore_result=True,
             rate_limit='10/m')
def get_last_tournaments(tournament_format: str, force: bool=False) -> None:
    """Gets the last tournaments that where published on mtgtop8 for the given format.

    Harvests the last tournaments url from every format main page. Crawl them if they are not already in database.
    """

    if tournament_format not in FORMATS:
        logger.error('Tournament format must be ({})'.format('|'.join(FORMATS)))
        return

    logger.debug('Fetching main page for format {}...'.format(tournament_format))
    try:
        r = requests.get(MTG_TOP8_URL + 'format?f=' + tournament_format)
    except Exception as err:
        logger.error(err)
        raise

    logger.debug('Parsing main page for format {}...'.format(tournament_format))
    soup = BeautifulSoup(r.text, 'html.parser')

    for tournament in parse_tournaments(soup):

            logger.debug(
                'Handling tournament {} ({}) at url {}...'.format(
                    tournament['name'],
                    tournament['date'],
                    tournament['url']
                )
            )

            format_obj, _ = Format.objects.get_or_create(name=FORMATS[tournament_format])

            logger.debug('Checking in database for tournament {}'.format(tournament['id']))
            tournament_obj, created = Tournament.objects.get_or_create(
                id=tournament['id'],
                defaults={
                    'name': tournament['name'],
                    'format': format_obj,
                    'event_date': tournament['date']
                }
            )

            if created or force:
                logger.info('Tournament {} ({}) does not exists yet. Crawling it...'.format(
                    tournament['id'], tournament['url']))
                get_tournament.delay(tournament['url'])
            else:
                logger.info('Tournament {} ({}) already exists. Skipping'.format(tournament['id'], tournament['url']))


@shared_task(soft_time_limit=5,
             name='Harvest all tournaments',
             ignore_result=True)
def harvest_formats(force: bool=False) -> None:
    """Main function to crawl the last tournament. Simple calls get_last_tournaments on main formats.

    If force is set to False, tournaments already in database will not be crawled.
    """

    group(get_last_tournaments.s(f, force) for f in FORMATS)()
