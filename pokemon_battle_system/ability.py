"""Ability class for Pokémon battle system."""
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, List

@dataclass
class Ability:
    """Represents an ability that a Pokémon can have.
    
    Attributes:
        name (str): The name of the ability
        description (str): Description of what the ability does
        on_start (callable, optional): Called when the battle starts
        on_switch_in (callable, optional): Called when the Pokémon switches in
        on_damage (callable, optional): Called when the Pokémon takes damage
        on_after_move (callable, optional): Called after the Pokémon uses a move
        on_before_move (callable, optional): Called before the Pokémon uses a move
        on_faint (callable, optional): Called when the Pokémon faints
        on_weather_change (callable, optional): Called when the weather changes
        on_terrain_change (callable, optional): Called when the terrain changes
        on_status_apply (callable, optional): Called when a status is applied
        on_stat_change (callable, optional): Called when a stat changes
    """
    name: str
    description: str
    on_start: Optional[Callable] = None
    on_switch_in: Optional[Callable] = None
    on_damage: Optional[Callable] = None
    on_after_move: Optional[Callable] = None
    on_before_move: Optional[Callable] = None
    on_faint: Optional[Callable] = None
    on_weather_change: Optional[Callable] = None
    on_terrain_change: Optional[Callable] = None
    on_status_apply: Optional[Callable] = None
    on_stat_change: Optional[Callable] = None
    
    def __str__(self) -> str:
        """Return a string representation of the ability."""
        return f"{self.name}: {self.description}"

# Common abilities
def create_ability(name: str, description: str, **kwargs) -> Ability:
    """Helper function to create an ability with the given callbacks.
    
    Args:
        name (str): Name of the ability
        description (str): Description of the ability
        **kwargs: Callback functions for the ability
        
    Returns:
        Ability: A new Ability instance
    """
    return Ability(name=name, description=description, **kwargs)

# Example abilities
INTIMIDATE = create_ability(
    name="Intimidate",
    description="Lowers the foe's Attack stat when the Pokémon enters battle.",
    on_switch_in=lambda battle, pokemon: battle.lower_stat(pokemon, 'attack', 1)
)

LEVITATE = create_ability(
    name="Levitate",
    description="Gives immunity to Ground-type moves.",
    on_damage=lambda battle, target, move, damage: 0 if move.type.lower() == 'ground' else damage
)

SPEED_BOOST = create_ability(
    name="Speed Boost",
    description="The Pokémon's Speed stat is raised at the end of each turn.",
    on_after_move=lambda battle, pokemon: battle.boost_stat(pokemon, 'speed', 1)
)

# Dictionary of all abilities
ABILITIES = {
    'intimidate': INTIMIDATE,
    'levitate': LEVITATE,
    'speed_boost': SPEED_BOOST,
    # Add more abilities as needed
}

def get_ability(name: str) -> Optional[Ability]:
    """Get an ability by name.
    
    Args:
        name (str): Name of the ability (case-insensitive)
        
    Returns:
        Optional[Ability]: The ability if found, None otherwise
    """
    return ABILITIES.get(name.lower())
