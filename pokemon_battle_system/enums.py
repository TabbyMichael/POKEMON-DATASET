"""Enums for Pokémon battle system."""

from enum import Enum, auto

class MoveCategory(Enum):
    """Categories of moves in Pokémon battles."""
    PHYSICAL = "Physical"
    SPECIAL = "Special"
    STATUS = "Status"

class Weather(Enum):
    """Weather conditions that can affect battles."""
    CLEAR = "Clear Skies"
    RAIN = "Rain"
    HARSH_SUN = "Harsh Sunlight"
    SANDSTORM = "Sandstorm"
    HAIL = "Hail"
    FOG = "Fog"

class Terrain(Enum):
    """Battle terrains that can affect battles."""
    NONE = "None"
    ELECTRIC = "Electric Terrain"
    GRASSY = "Grassy Terrain"
    MISTY = "Misty Terrain"
    PSYCHIC = "Psychic Terrain"

class SideCondition(Enum):
    """Conditions that affect one side of the battlefield."""
    SPIKES = "Spikes"
    TOXIC_SPIKES = "Toxic Spikes"
    STEALTH_ROCK = "Stealth Rock"
    STICKY_WEB = "Sticky Web"
    TAILWIND = "Tailwind"
    LIGHT_SCREEN = "Light Screen"
    REFLECT = "Reflect"
    AURORA_VEIL = "Aurora Veil"

class StatusCondition(Enum):
    """Non-volatile status conditions in Pokémon battles."""
    NONE = None
    POISON = "poison"
    TOXIC = "toxic"
    BURN = "burn"
    FREEZE = "freeze"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FAINTED = "fainted"

class VolatileStatus(Enum):
    """Volatile status conditions in Pokémon battles."""
    CONFUSED = "confused"
    FLINCH = "flinch"
    LEECH_SEED = "leech_seed"
    PERISH_SONG = "perish_song"
    TAUNT = "taunt"
    ENCORE = "encore"
    DISABLE = "disable"
    TORMENT = "torment"
    IDENTIFIED = "identified"  # For Foresight, Odor Sleuth, etc.
    TELEKINESIS = "telekinesis"
    HEAL_BLOCK = "heal_block"
    EMBARGO = "embargo"
    POWER_TRICK = "power_trick"
    ILLUSION = "illusion"  # For Zorua/Zoroark
    AQUA_RING = "aqua_ring"
    ROOTED = "rooted"  # For Ingrain
    MAGIC_COAT = "magic_coat"
    SUBSTITUTE = "substitute"
    DESTINY_BOND = "destiny_bond"
    GRUDGE = "grudge"
    NIGHTMARE = "nightmare"
    CURSED = "cursed"
    EMBER = "ember"  # For Fire Spin, etc.
    WRAP = "wrap"  # For Wrap, Bind, etc.
    MINIMIZE = "minimize"  # For Stomp, etc.
    CHARGING = "charging"  # For Solar Beam, etc.
    RECHARGE = "recharge"  # For Hyper Beam, etc.
    RAMPAGE = "rampage"  # For Thrash, Outrage, etc.
    PROTECT = "protect"  # For Protect, Detect, etc.
    ENDURE = "endure"  # For Endure
    FOCUS_ENERGY = "focus_energy"  # For Focus Energy
    LOCKED_IN = "locked_in"  # For Choice items
    MAGNET_RISE = "magnet_rise"  # For Magnet Rise
