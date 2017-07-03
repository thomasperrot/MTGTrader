"""
@author: Thomas PERROT

Contains models for cards app
"""


from datetime import date, timedelta
from urllib.parse import quote_plus

from django.db import models
from django.core import validators

from sets.models import Set, Rarity


class Color(models.Model):
    """Class which represents a color.
    """

    COLORS_NAME = (
        ('white', 'White'),
        ('blue', 'Blue'),
        ('black', 'Black'),
        ('red', 'Red'),
        ('green', 'Green'),
    )
    COLORS_ID = (
        ('W', 'White'),
        ('U', 'Blue'),
        ('B', 'Black'),
        ('R', 'Red'),
        ('G', 'Green'),
    )

    color_id = models.CharField(max_length=1, primary_key=True, choices=COLORS_ID)

    def __str__(self) -> str:
        return self.name.capitalize()

    @property
    def name(self) -> str:
        return self.get_color_id_display().lower()


class Type(models.Model):
    """Class which represents a card type (e.g creature, sorcery, etc.).
    """

    TYPES = (
        ('creature', 'Creature'),
        ('sorcery', 'Sorcery'),
        ('instant', 'Instant'),
        ('enchantment', 'Enchantment'),
        ('artifact', 'Artifact'),
        ('land', 'Land'),
        ('tribal', 'Tribal'),
        ('planeswalker', 'Planeswalker'),
    )

    name = models.CharField(max_length=50, primary_key=True, choices=TYPES)

    def __str__(self) -> str:
        return self.get_name_display()


class SuperType(models.Model):
    """Class which represents a card supertype  (Basic, Legendary, Snow, World, Ongoing, etc.).
    """

    TYPES = (
        ('legendary', 'Legendary'),
        ('basic', 'Basic'),
        ('world', 'World'),
        ('snow', 'Snow'),
        ('ongoing', 'Ongoing')
    )

    name = models.CharField(max_length=50, primary_key=True, choices=TYPES)

    def __str__(self) -> str:
        return self.get_name_display()


class SubType(models.Model):
    """Class which represents a card subtype (e.g warrior, human, etc.).
    """

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self) -> str:
        return self.name.capitalize()

    class Meta:
        verbose_name = 'Subtype'
        verbose_name_plural = 'Subtypes'
        ordering = ['name']


class CardName(models.Model):
    """Class which represents a card name.
    """

    name = models.CharField(max_length=50, primary_key=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'Cards name'
        ordering = ['name']


class Card(models.Model):
    """Class which represents a card. It has the following attributes (from docs.magicthegathering.io):

        - id	    A unique id for this card. It is made up by doing an SHA1 hash of setCode + cardName + cardImageName

        - name		The card name. For split, double-faced and flip cards, just the name of one side of the card.
                    Basically each ‘sub-card’ has its own record.

        - names  	Only used for split, flip and dual cards. Will contain all the names on this card, front or back.

        - mana_cost	The mana cost of this card. Consists of one or more mana symbols.

        - layout	The card layout. Possible values: normal, split, flip, double-faced, token, plane, scheme,
                    phenomenon, leveler, vanguard

        - cmc		Converted mana cost. Always a number.

        - colors	The card colors. Usually this is derived from the casting cost,
                    but some cards are special (like the back of dual sided cards and Ghostfire).

        - colors_identity	 The card colors by color code. [“Red”, “Blue”] becomes [“R”, “U”]

        - type		The card type. This is the type you would see on the card if printed today. Note: The dash is
                    a UTF8 'long dash’ as per the MTG rules. We derive it from supertypes, types and subtypes.

        - supertypes The supertypes of the card. These appear to the far left of the card type.
                     Example values: Basic, Legendary, Snow, World, Ongoing

        - types     The types of the card. These appear to the left of the dash in a card type.
                    Example values: Instant, Sorcery, Artifact, Creature, Enchantment, Land, Planeswalker

        - subtypes	The subtypes of the card. These appear to the right of the dash in a card type.
                    Usually each word is its own subtype. Example values: Trap, Arcane, Equipment, Aura, etc.

        - rarity	The rarity of the card. Examples: Common, Uncommon, Rare, Mythic Rare, Special, Basic Land

        - set		The set the card belongs to.

        - text		The oracle text of the card. May contain mana symbols and other symbols.

        - flavor	The flavor text of the card.

        - artist	The artist of the card. This may not match what is on the card as MTGJSON
                    corrects many card misprints.

        - number	The card number. This is printed at the bottom-center of the card in small text.
                    This is a string, not an integer, because some cards have letters in their numbers.

        - power		The power of the card. This is only present for creatures.
                    This is a string, not an integer, because some cards have powers like: “1+-”

        - toughness	The toughness of the card. This is only present for creatures.
                    This is a string, not an integer, because some cards have toughness like: “1+-”

        - loyalty	The loyalty of the card. This is only present for planeswalkers.

        - foreign_names  Foreign language names for the card, if this card in this set was printed in another
                         language. An array of objects, each object having 'language’, 'name’ and 'multiverseid’
                         keys. Not available for all sets.

        - language	The language the card is printed in. Use this parameter when searching by foreignName

        - gameFormat    The game format, such as Commander, Standard, Legacy, etc.
                        (when used, legality defaults to Legal unless supplied)

        - multiverse_id	   The multiverseid of the card on Wizard’s Gatherer web page. Cards from sets that do not
                           exist on Gatherer will NOT have a multiverseid. Sets not on Gatherer are: ATH, ITP, DKM,
                           RQS, DPA and all sets with a 4 letter code that starts with a lowercase 'p’.

        - variations	If a card has alternate art (for example, 4 different Forests, or the 2 Brothers Yamazaki)
                        then each other variation’s multiverse_id will be listed here, NOT including the current
                        card’s multiverseid.

        - image_url	The image url for a card. Only exists if the card has a multiverse id.

        - watermark	The watermark on the card. Note: Split cards don’t currently have this field set, despite
                    having a watermark on each side of the split card.

        - border	If the border for this specific card is DIFFERENT than the border specified in the top level
                    set, then it will be specified here. (Example: Unglued has silver borders, except for
                    the lands which are black bordered).

        - source	For promo cards, this is where this card was originally obtained. For box sets that are
                theme decks, this is which theme deck the card is from.

        - timeshifted	If this card was a timeshifted card in the set.

        - hand	Maximum hand size modifier. Only exists for Vanguard cards.

        - life	Starting life total modifier. Only exists for Vanguard cards.

        - reserved	Set to true if this card is reserved by Wizards Official Reprint Policy

        - release_date	The date this card was released. This is only set for promo cards. The date may not be
                        accurate to an exact day and month, thus only a partial date may be set
                        (YYYY-MM-DD or YYYY-MM or YYYY). Some promo cards do not have a known release date.

        - starter   Set to true if this card was only released as part of a core box set. These are technically
                    part of the core sets and are tournament legal despite not being available in boosters.

        - rulings	The rulings for the card. An array of objects, each object having 'date’ and 'text’ keys.

        - printings	 The sets that this card was printed in.

        - original_text	The original text on the card at the time it was printed. This field is not available for
                        promo cards.

        - original_type	The original type on the card at the time it was printed. This field is not available for
                        promo cards.
    """

    LAYOUT = (
        ('normal', 'Normal'),
        ('split', 'Split'),
        ('flip', 'Flip'),
        ('meld', 'Meld'),
        ('double-faced', 'Double-faced'),
        ('token', 'Token'),
        ('plane', 'Plane'),
        ('scheme', 'Scheme'),
        ('phenomenon', 'Phenomenon'),
        ('leveler', 'Leveler'),
        ('vanguard', 'Vanguard'),
        ('aftermath', 'Aftermath')
    )
    MKM_BASE_CARD_URL = 'http://www.magiccardmarket.eu/Products/Singles/{set}/{card_name}'

    # Mandatory fields
    id = models.CharField(max_length=50, primary_key=True)
    name = models.ForeignKey(CardName, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    printings = models.ManyToManyField(Set, related_name='+')  # conflict with self.set
    artist = models.CharField(max_length=50)
    layout = models.CharField(max_length=15, choices=LAYOUT, default='normal')

    # Specific card fields
    power = models.CharField(max_length=20, blank=True)
    toughness = models.CharField(max_length=20, blank=True)
    loyalty = models.CharField(max_length=10, blank=True)
    names = models.ManyToManyField(CardName, blank=True, related_name='+')  # conflict with self.name
    mana_cost = models.CharField(max_length=50, blank=True)
    cmc = models.PositiveSmallIntegerField(blank=True, null=True)
    colors = models.ManyToManyField(Color, blank=True)
    colors_identity = models.ManyToManyField(Color, blank=True, related_name='+')  # conflict with colors
    types = models.ManyToManyField(Type, blank=True)
    sub_types = models.ManyToManyField(SubType, blank=True)
    super_types = models.ManyToManyField(SuperType, blank=True)
    text = models.CharField(max_length=500, blank=True)
    flavor = models.CharField(max_length=500, blank=True)
    border = models.CharField(max_length=6, choices=Set.BORDER, default='black', blank=True)

    # Optional meta fields
    multiverse_id = models.PositiveIntegerField(blank=True, null=True)
    mkm_name = models.CharField(max_length=100, blank=True)
    image_url = models.CharField(max_length=100, blank=True, validators=[validators.URLValidator])
    original_text = models.CharField(max_length=500, blank=True)
    original_type = models.CharField(max_length=500, blank=True)

    # Exotic fields
    number = models.CharField(max_length=25, blank=True)
    source = models.CharField(max_length=100, blank=True)
    timeshifted = models.BooleanField(blank=True, default=False)
    hand = models.SmallIntegerField(blank=True, null=True)
    life = models.SmallIntegerField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    starter = models.BooleanField(blank=True, default=False)
    variations = models.CharField(max_length=200, blank=True, validators=[
        validators.validate_comma_separated_integer_list])

    # Additional fields for app behavior
    is_relevant = models.BooleanField(default=False)

    def __str__(self) -> str:
        return '{} - {}'.format(self.name.name, self.set.id)

    class Meta:
        ordering = ['name']

    @property
    def type(self) -> str:
        """Returns the complete type a the card.

        e.g. `Legendary Echantment Creature — God`
        """

        result = ''
        if self.super_types:
            result += ' '.join([t.name for t in self.super_types])
        result += ' '.join(sorted([t.name for t in self.types]))
        if self.sub_types:
            result += ' — ' + ' '.join(sorted([t.name for t in self.sub_types]))
        return result

    @property
    def mkm_url(self) -> str:
        """Returns the magiccardmarket.eu url for this card.
        """

        if self.mkm_name:
            card_name = self.mkm_name
        elif self.layout in ('double-faced', 'meld'):
            card_name = ' / '.join(n.name for n in self.names.all())
        elif self.layout in ('aftermath', 'split'):
            card_name = ' // '.join(n.name for n in self.names.all())
        else:
            card_name = self.name.name

        set_name = self.set.mkm_name or self.set.name

        url = self.MKM_BASE_CARD_URL.format(
            set=quote_plus(set_name),
            card_name=quote_plus(card_name)
        )

        return url

    @property
    def was_played_recently(self) -> bool:
        """Returns whether the card was played in a major tournament for last 2 months.
        """

        for deck_to_card in self.name.decktocard_set:
            for deck_position in deck_to_card.deck.deckposition_set:
                if deck_position.tournament.event_date > date.today() - timedelta(days=60):
                    return True
        return False
