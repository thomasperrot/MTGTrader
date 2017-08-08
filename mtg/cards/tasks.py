"""
@author: Thomas PERROT

Contains tasks for cards app
"""


from typing import Dict
import re
from collections import Counter
from datetime import datetime

import requests
from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from celery.utils.log import get_task_logger
from django.utils import timezone

from .models import Set, CardName, Card, Color, Type, SubType, SuperType
from sets.models import Rarity, Slot, Booster
from tournaments.models import Format, Legality

logger = get_task_logger(__name__)

MTG_URL_CARDS = 'https://api.magicthegathering.io/v1/cards?page={page}&pageSize={page_size}'
MTG_URL_CARDS_BY_SET = 'https://api.magicthegathering.io/v1/cards?set={set_id}'
MTG_URL_SETS = 'https://api.magicthegathering.io/v1/sets'


def to_snake_case(name: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def post_process_card(card: Dict) -> None:
    """Add some attributes to the card before storing it.
    """

    # Char issues
    if card['name'] == 'Aether Vial':
        card['mkm_name'] = 'Æther Vial'

    # Version issues
    conditions = (
        lambda x: x['name'] == "Atraxa, Praetors' Voice",
        lambda x: x['name'] == 'Saskia the Unyielding',
        lambda x: x['name'] == "Kaya, Ghost Assassin" and x['number'] == 75,
        lambda x: x['name'] == "Meren of Clan Nel Toth" and x['set'].id == 'C15',
        lambda x: x['name'] == "Derevi, Empyrial Tactician" and x['set'].id == 'C13'
    )
    if any(conditions):
        card['mkm_name'] = card['name'] + ' (Version 1)'

    conditions = (
        lambda x: x['name'] == "Kaya, Ghost Assassin" and x['number'] == 222,
    )
    if any(conditions):
        card['mkm_name'] = card['name'] + ' (Version 2)'

    # Layout issue
    mkm_names = (
        "Mayor of Avabruck / Howlpack Alpha",
        "Jace, Vryn's Prodigy // Jace, Telepath Unbound",
        'Westvale Abbey / Ormendahl, Profane Prince',
        'Thing in the Ice / Awoken Horror',
        'Arlinn Kord / Arlinn, Embraced by the Moon',
        'Dusk // Dawn',
        'Heaven // Earth',
        'Gisela, the Broken Blade / Brisela, Voice of Nightmares',
        'Hanweir Battlements / Hanweir, the Writhing Township',
        'Hanweir Garrison / Hanweir, the Writhing Township',
        'Driven // Despair',
        'Voldaren Pariah / Abolisher of Bloodlines'
    )
    name_to_mkm_name = {subname.strip(): name for name in mkm_names for subname in name.split('/') if subname}
    if card['name'] in name_to_mkm_name:
        card['mkm_name'] = name_to_mkm_name.get(card['name'], '')


def post_process_set(set_: Dict) -> None:
    """Add some attributes to the card before storing it.
    """

    if set_['id'] in ('ATQ', 'VMA', 'MED', 'ME2', 'ME3', 'ME4', 'TPR',):
        set_['is_relevant'] = False
    elif set_['id'] == 'MM3':
        set_['mkm_name'] = 'Modern Masters 2017'
    elif set_['id'] == 'DPA':
        set_['mkm_name'] = 'Duels of the Planeswalkers Decks'


def parse_rarity(rarity: str) -> Dict:
    """Converts booster rarity to card rarity, which are not always the same (damn wizard...).
    """

    if rarity == 'foil':
        return {'rarity': 'C', 'foil': True}

    if rarity.startswith('foil'):
        foil = True
        rarity = rarity[5:]
    else:
        foil = False

    rarity_conversion = {
        'land': 'B',
        'marketing': 'S',
        'checklist': 'S',
        'draft-matters': 'S',
        'power nine': 'R',
        'double faced': 'S',
        'double faced common': 'C',
        'double faced uncommon': 'U',
        'double faced rare': 'R',
        'double faced mythic rare': 'M',
        'timeshifted purple': 'S',
        'timeshifted common': 'C',
        'timeshifted uncommon': 'U',
        'timeshifted rare': 'R',
    }
    rarity = rarity_conversion.get(rarity, '') or rarity

    return {'rarity': rarity[0].upper(), 'foil': foil}


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Store booster',
             ignore_result=True)
def store_booster(set_dict: Dict) -> None:
    """Fills boosters table from sets collection.
    """

    s = Set.objects.get(id=set_dict['code'])
    booster = Booster.objects.get_or_create(set=s)[0]
    booster_slots = []

    single_slots = [s for s in set_dict['booster'] if isinstance(s, str)]
    multi_slots = [s for s in set_dict['booster'] if isinstance(s, list)]

    for rarity, number in Counter(single_slots).items():
        slot = Slot.objects.get_or_create(number=number, booster=booster)[0]
        rarity = Rarity.objects.get_or_create(**parse_rarity(rarity))[0]
        slot.rarities.add(rarity)
        slot.save()
        booster_slots.append(slot)

    for multi_slot in multi_slots:
        slot = Slot.objects.get_or_create(number=1, booster=booster)[0]
        for rarity in multi_slot:
            rarity = Rarity.objects.get_or_create(**parse_rarity(rarity))[0]
            slot.rarities.add(rarity)
        slot.save()
        booster_slots.append(slot)


def parse_set(s: Dict) -> Dict:
    """Parses the given set.
    """

    formated_set = {}
    for key, value in s.items():
        formated_set[to_snake_case(key)] = value
    formated_set['id'] = formated_set.pop('code')
    formated_set['has_booster'] = bool(formated_set.pop('booster', False))
    d = datetime.strptime(formated_set.pop('release_date'), '%Y-%m-%d')
    formated_set['release_date'] = timezone.make_aware(d, timezone.get_current_timezone())

    return formated_set


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Harvest all sets',
             ignore_result=True)
def harvest_sets() -> None:
    """Harvests all sets, stores them, and create associated booster if needed.

    Also creates Rarity and Slot (from Booster creation) if set does not already exists.
    """

    logger.info('Starting to harvest sets.')

    r = requests.get(MTG_URL_SETS)
    json_resp = r.json()
    sets = json_resp['sets']

    for set_dict in sets:

        logger.info('Saving set {}.'.format(set_dict['name']))
        parsed_set = parse_set(set_dict)
        post_process_set(parsed_set)

        set_id = parsed_set.pop('id')

        set_, created = Set.objects.get_or_create(id=set_id, defaults=parsed_set)

        logger.info('Creating booster for set {}.'.format(set_dict['name']))
        if created:
            harvest_cards.delay(set_id=set_.id)
            if set_.has_booster:
                store_booster.delay(set_dict)


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             name='Store card',
             ignore_result=True,)
def store_card(card: Dict) -> None:
    """Parse card and stores it in database.
    """

    post_process_card(card)

    c = {
        'id': card['id'],
        'name': CardName.objects.get_or_create(name=card['name'])[0],
        'rarity': Rarity.objects.get_or_create(**parse_rarity(card['rarity']))[0],
        'set': Set.objects.get(id=card['set']),
        'artist': card['artist'],
        'layout': card['layout'],
    }

    for attr in ['power', 'toughness', 'loyalty', 'mana_cost', 'cmc', 'text', 'flavor', 'border', 'multiverse_id',
                 'image_url', 'original_text', 'original_type', 'number', 'source', 'timeshifted', 'hand', 'life',
                 'starter', 'mkm_name']:
        if attr in card:
            c[attr] = card[attr]

    if 'release_date' in card:
        d = None
        for f in ['%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                d = datetime.strptime(card['release_date'], f)
            except ValueError:
                pass
            else:
                break
        if d:
            c['release_date'] = timezone.make_aware(d, timezone.get_current_timezone())

    card_obj, created = Card.objects.get_or_create(id=c['id'], defaults=c)

    if not created:
        logger.debug('Card {} already exists. Skipping.'.format(card_obj.name.name))
        return

    logger.debug('Card {} does not exists yet. Saving all associated data.'.format(card_obj.name.name))

    for set_id in card.get('printings', []):
        s = Set.objects.get(id=set_id)
        card_obj.printings.add(s)
    for name in card.get('names', []):
        n = CardName.objects.get_or_create(name=name)[0]
        card_obj.names.add(n)
    for color in card.get('colors', []):
        c = Color.objects.get_or_create(color_id=color[0].upper())[0]
        card_obj.colors.add(c)
    for color_identity in card.get('color_identity', []):
        c = Color.objects.get_or_create(color_id=color_identity[0].upper())[0]
        card_obj.colors_identity.add(c)
    for type_name in card.get('types', []):
        t = Type.objects.get_or_create(name=type_name.lower())[0]
        card_obj.types.add(t)
    for subtype_name in card.get('subtypes', []):
        t = SubType.objects.get_or_create(name=subtype_name.lower())[0]
        card_obj.sub_types.add(t)
    for supertype_name in card.get('supertypes', []):
        t = SuperType.objects.get_or_create(name=supertype_name.lower())[0]
        card_obj.super_types.add(t)
    for legality in card.get('legalities', []):
        f = Format.objects.get_or_create(name=legality['format'].lower())[0]
        l = Legality(card=card_obj, format=f, legality=legality['legality'])
        l.save()

    card_obj.save()


@shared_task(soft_time_limit=5,
             autoretry_for=(ConnectionError, SoftTimeLimitExceeded),
             default_retry_delay=3,
             retry_kwargs={'max_retries': 5},
             rate_limit='10/m',
             name='Harvest cards',
             ignore_result=True)
def harvest_cards(page: int=1, set_id: str=None) -> None:
    """Harvests card from MTG API, and stores them in database.
    """

    logger.info('Starting to harvest cards.')

    if set_id:
        r = requests.get(MTG_URL_CARDS_BY_SET.format(set_id=set_id))
    else:
        r = requests.get(MTG_URL_CARDS.format(page=page, page_size=100))
    r.raise_for_status()

    cards = r.json()['cards']
    if cards and not set_id:
        logger.info('Trying to query page {}'.format(page))
        harvest_cards.delay(page + 1)

    for card in cards:
        logger.info('Storing card {}...'.format(card['name']))
        formated_card = {}
        for key, value in card.items():
            formated_card[to_snake_case(key)] = value
        store_card.delay(formated_card)
