"""
@author: Thomas PERROT

Contains models for sets app
"""


from django.db import models


class Rarity(models.Model):
    """Class which represents a card rarity.
    """

    RARITY = (
        ('C', 'Common'),
        ('U', 'Uncommon'),
        ('R', 'Rare'),
        ('M', 'Mythic Rare'),
        ('S', 'Special'),
        ('B', 'Basic Land')
    )

    rarity = models.CharField(max_length=15, choices=RARITY)
    foil = models.BooleanField(default=False)

    def __str__(self) -> str:
        s = self.get_rarity_display().lower()
        if self.foil:
            s += ' (Foil)'
        return s

    def short(self) -> str:
        s = self.rarity
        if self.foil:
            s += ' (F)'
        return s

    class Meta:
        verbose_name_plural = 'Rarities'
        ordering = ['rarity', 'foil']
        unique_together = ("rarity", "foil")


class Set(models.Model):
    """Class which represents a cards set.
    """

    TYPE = (
        # Traditional sets
        ('core', 'Core'),  # M11, M12, etc.
        ('expansion', 'Expansion'),
        ('un', 'Un'),  # Unglued & Unhinged
        ('conspiracy', 'Conspiracy'),
        ('masters', 'Masters'),
        ('reprint', 'Reprint'),  # Modern Masters, Eternal Masters, etc.

        # Boxes and decks
        ('box', 'Box'),
        ('from the vault', 'From the Vault'),
        ('planechase', 'Planechase'),
        ('duel deck', 'Duel Deck'),
        ('premium deck', 'Premium Deck'),
        ('commander', 'Commander'),

        # Others
        ('promo', 'Promo'),
        ('starter', 'Starter'),
        ('vanguard', 'Vanguard'),
        ('archenemy', 'Archenemy'),
        ('masterpiece', 'Masterpiece')
    )

    BORDER = (
        ('white', 'White'),
        ('silver', 'Silver'),
        ('black', 'Black'),
    )

    # Mandatory fields
    id = models.CharField(max_length=25, primary_key=True)
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=TYPE)
    release_date = models.DateField()
    border = models.CharField(max_length=6, choices=BORDER)

    # Optional fields
    block = models.CharField(max_length=50, blank=True)
    has_booster = models.BooleanField(blank=True, default=False)
    gatherer_code = models.CharField(max_length=50, blank=True)
    mkm_id = models.PositiveIntegerField(blank=True, null=True)
    mkm_name = models.CharField(max_length=50, blank=True)
    magic_cards_info_code = models.CharField(max_length=50, blank=True)
    old_code = models.CharField(max_length=25, blank=True)
    online_only = models.BooleanField(blank=True, default=False)

    # Additional fields for app behavior
    is_relevant = models.BooleanField(default=True)

    def __str__(self) -> str:
        return '{} ({})'.format(self.name, self.id)

    class Meta:
        ordering = ['-release_date']


class Booster(models.Model):
    """Class which represents a booster.
    """

    set = models.ForeignKey(Set, on_delete=models.CASCADE, limit_choices_to={'has_booster': True})

    def __str__(self) -> str:
        return self.set.name


class Slot(models.Model):
    """Class which represent s slot in a booster.

    Some boosters can have different rarities in the same slot.
    e.g: for MM3 boosters :
        - "rare" OR "mythic rare",
        - "uncommon" x 3,
        - "common" x 10,
        - "foil mythic rare" OR "foil rare" OR "foil uncommon" OR "foil common"
    """

    booster = models.ForeignKey(Booster, on_delete=models.CASCADE)
    rarities = models.ManyToManyField(Rarity)
    number = models.PositiveSmallIntegerField()

    def __str__(self) -> str:
        rarities = ' / '.join(r.short() for r in self.rarities.all())
        return '{}: {} ({})'.format(self.booster.set.name, rarities, self.number)
