from pprint import pprint
from datetime import datetime

import pytest
from bs4 import BeautifulSoup
from django.utils import timezone

from ..tasks import parse_mw_deck, parse_tournament


def test_parse_tournament():
    """Asserts that bs4 tags for a given tournament are correctly parsed.
    """

    bs4_tag = """<tr height="30" class="hover_tr">
    <td width="70%"><a href="event?e=15191&amp;f=MO">MTGO Competitive Modern Constructed League</a> <img src="graph/new.png"></td>
    <td width="15%" class="O16" align="center"><img src="graph/star.png"></td>
    <td align="right" width="15%" class="S10">06/04/17</td>
    </tr>'"""

    bs4_tournament_tag = BeautifulSoup(bs4_tag, 'html.parser')

    parsed = parse_tournament(bs4_tournament_tag)
    date = timezone.make_aware(datetime(year=2017, month=4, day=6))

    assert parsed == {
        'id': '15191',
        'name': 'MTGO Competitive Modern Constructed League',
        'url': 'http://mtgtop8.com/event?e=15191&f=MO',
        'date': date
    }


content_mw_deck_1 = """// Deck file for Magic Workstation created with mtgtop8.com
// NAME : Sultai
// CREATOR : Sebastian Ziller
// FORMAT :
        1 [] Blooming Marsh
        1 [GTC] Breeding Pool
        1 [UNH] Forest
        1 [C15] Ghost Quarter
        1 [GTC] Godless Shrine
        1 [OGW] Hissing Quagmire
        1 [BFZ] Lumbering Falls
        1 [RTR] Overgrown Tomb
        1 [UNH] Swamp
        1 [RTR] Temple Garden
        1 [EVE] Twilight Mire
        1 [GTC] Watery Grave
        2 [WWK] Creeping Tar Pit
        2 [SOM] Darkslick Shores
        2 [ZEN] Misty Rainforest
        2 [KTK] Polluted Delta
        3 [ZEN] Verdant Catacombs
        2 [EMN] Grim Flayer
        2 [OGW] Kalitas, Traitor of Ghet
        2 [] Scavenging Ooze
        2 [ISD] Snapcaster Mage
        3 [RAV] Dark Confidant
        4 [FUT] Tarmogoyf
        4 [ISD] Liliana of the Veil
        1 [FD] Engineered Explosives
        3 [RTR] Abrupt Decay
        3 [] Fatal Push
        1 [EMN] Collective Brutality
        2 [ARB] Maelstrom Pulse
        2 [THS] Thoughtseize
        3 [] Inquisition of Kozilek
        3 [] Serum Visions
SB:  1 [NPH] Elesh Norn, Grand Cenobite
SB:  4 [CHK] Gifts Ungiven
SB:  1 [ZEN] Iona, Shield of Emeria
SB:  3 [10E] Rain of Tears
SB:  3 [NPH] Surgical Extraction
SB:  1 [ISD] Unburial Rites
SB:  2 [THS] Ashiok, Nightmare Weaver"""

parsed_result_1 = {
    'cards': {
        'Abrupt Decay': 3,
        'Blooming Marsh': 1,
        'Breeding Pool': 1,
        'Collective Brutality': 1,
        'Creeping Tar Pit': 2,
        'Dark Confidant': 3,
        'Darkslick Shores': 2,
        'Engineered Explosives': 1,
        'Fatal Push': 3,
        'Forest': 1,
        'Ghost Quarter': 1,
        'Godless Shrine': 1,
        'Grim Flayer': 2,
        'Hissing Quagmire': 1,
        'Inquisition of Kozilek': 3,
        'Kalitas, Traitor of Ghet': 2,
        'Liliana of the Veil': 4,
        'Lumbering Falls': 1,
        'Maelstrom Pulse': 2,
        'Misty Rainforest': 2,
        'Overgrown Tomb': 1,
        'Polluted Delta': 2,
        'Scavenging Ooze': 2,
        'Serum Visions': 3,
        'Snapcaster Mage': 2,
        'Swamp': 1,
        'Tarmogoyf': 4,
        'Temple Garden': 1,
        'Thoughtseize': 2,
        'Twilight Mire': 1,
        'Verdant Catacombs': 3,
        'Watery Grave': 1
    },
    'format': 'MO',
    'name': 'Sultai',
    'owner': 'Sebastian Ziller',
    'sideboard': {
        'Ashiok, Nightmare Weaver': 2,
        'Elesh Norn, Grand Cenobite': 1,
        'Gifts Ungiven': 4,
        'Iona, Shield of Emeria': 1,
        'Rain of Tears': 3,
        'Surgical Extraction': 3,
        'Unburial Rites': 1
    }
}

content_mw_deck_2 = """// Deck file for Magic Workstation created with mtgtop8.com
// NAME : Abzan
// CREATOR : Luca Chieregato
// FORMAT :
        1 [UNH] Forest
        1 [GTC] Godless Shrine
        1 [RTR] Overgrown Tomb
        1 [UNH] Plains
        1 [WWK] Stirring Wildwood
        1 [UNH] Swamp
        1 [RTR] Temple Garden
        2 [BFZ] Shambling Vent
        2 [KTK] Windswept Heath
        3 [ZEN] Marsh Flats
        4 [] Blooming Marsh
        4 [ZEN] Verdant Catacombs
        2 [] Scavenging Ooze
        2 [KTK] Siege Rhino
        3 [EMN] Grim Flayer
        3 [CFX] Noble Hierarch
        4 [FUT] Tarmogoyf
        1 [EMN] Liliana, the Last Hope
        3 [ISD] Liliana of the Veil
        1 [C13] Nihil Spellbomb
        2 [RTR] Abrupt Decay
        3 [] Fatal Push
        3 [CMD] Path to Exile
        1 [ARB] Maelstrom Pulse
        3 [] Inquisition of Kozilek
        3 [THS] Thoughtseize
        4 [DKA] Lingering Souls
SB:  2 [BFZ] Gideon, Ally of Zendikar
SB:  3 [NPH] Surgical Extraction
SB:  2 [ISD] Stony Silence
SB:  1 [FD] Engineered Explosives
SB:  2 [EMN] Collective Brutality
SB:  3 [SHM] Fulminator Mage
SB:  1 [CMD] Path to Exile
SB:  1 [C13] Nihil Spellbomb"""

parsed_result_2 = {
    'cards': {
        'Abrupt Decay': 2,
        'Blooming Marsh': 4,
        'Fatal Push': 3,
        'Forest': 1,
        'Godless Shrine': 1,
        'Grim Flayer': 3,
        'Inquisition of Kozilek': 3,
        'Liliana of the Veil': 3,
        'Liliana, the Last Hope': 1,
        'Lingering Souls': 4,
        'Maelstrom Pulse': 1,
        'Marsh Flats': 3,
        'Nihil Spellbomb': 1,
        'Noble Hierarch': 3,
        'Overgrown Tomb': 1,
        'Path to Exile': 3,
        'Plains': 1,
        'Scavenging Ooze': 2,
        'Shambling Vent': 2,
        'Siege Rhino': 2,
        'Stirring Wildwood': 1,
        'Swamp': 1,
        'Tarmogoyf': 4,
        'Temple Garden': 1,
        'Thoughtseize': 3,
        'Verdant Catacombs': 4,
        'Windswept Heath': 2},
    'format': 'MO',
    'name': 'Abzan',
    'owner': 'Luca Chieregato',
    'sideboard': {
        'Collective Brutality': 2,
        'Engineered Explosives': 1,
        'Fulminator Mage': 3,
        'Gideon, Ally of Zendikar': 2,
        'Nihil Spellbomb': 1,
        'Path to Exile': 1,
        'Stony Silence': 2,
        'Surgical Extraction': 3
    }
}

content_mw_deck_3 = """// Deck file created with mtgtop8.com
// NAME : Affinity
// CREATOR : Mani_Davoudi
// FORMAT : Modern
4 [DS] Arcbound Ravager
2 [SOM] Etched Champion
2 [C16] Master of Etherium
2 [SOM] Memnite
4 [AER] Ornithopter
4 [MBS] Signal Pest
4 [M11] Steel Overseer
4 [NPH] Vault Skirge
4 [C16] Cranial Plating
4 [C16] Darksteel Citadel
4 [SOM] Mox Opal
4 [BNG] Springleaf Drum
1 [MR] Welding Jar
4 [SOM] Galvanic Blast
4 [DS] Blinkmoth Nexus
1 [MR] Glimmervoid
4 [MBS] Inkmoth Nexus
1 [RTR] Mountain
3 [AER] Spire of Industry
SB:  2 [SOM] Etched Champion
SB:  2 [ISD] Ancient Grudge
SB:  2 [NPH] Dispatch
SB:  2 [ORI] Ghirapur Aether Grid
SB:  1 [DKA] Grafdigger's Cage
SB:  2 [RTR] Rest in Peace
SB:  1 [ZEN] Spell Pierce
SB:  2 [THS] Thoughtseize
SB:  1 [DGM] Wear / Tear"""

parsed_result_3 = {
    'cards': {
        'Arcbound Ravager': 4,
        'Blinkmoth Nexus': 4,
        'Cranial Plating': 4,
        'Darksteel Citadel': 4,
        'Etched Champion': 2,
        'Galvanic Blast': 4,
        'Glimmervoid': 1,
        'Inkmoth Nexus': 4,
        'Master of Etherium': 2,
        'Memnite': 2,
        'Mountain': 1,
        'Mox Opal': 4,
        'Ornithopter': 4,
        'Signal Pest': 4,
        'Spire of Industry': 3,
        'Springleaf Drum': 4,
        'Steel Overseer': 4,
        'Vault Skirge': 4,
        'Welding Jar': 1
    },
    'format': 'MO',
    'name': 'Affinity',
    'owner': 'Mani_Davoudi',
    'sideboard': {
        'Ancient Grudge': 2,
        'Dispatch': 2,
        'Etched Champion': 2,
        'Ghirapur Aether Grid': 2,
        "Grafdigger's Cage": 1,
        'Rest in Peace': 2,
        'Spell Pierce': 1,
        'Thoughtseize': 2,
        'Wear / Tear': 1
    }
}


@pytest.mark.parametrize('content,expected', [
    (content_mw_deck_1, parsed_result_1),
    (content_mw_deck_2, parsed_result_2),
    (content_mw_deck_3, parsed_result_3),
], ids=list(map(str, range(2))))
def test_parse_mw_deck(content, expected):
    """Asserts that mwDeck contents are correctly parsed.
    """

    parsed = parse_mw_deck(content)
    pprint(parsed)
    assert parsed == expected
