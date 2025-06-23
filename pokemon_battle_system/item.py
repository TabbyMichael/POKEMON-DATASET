"""Item class for Pokémon battle system."""
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict, Any, List

@dataclass
class Item:
    """Represents a held item that a Pokémon can have.
    
    Attributes:
        name (str): The name of the item
        description (str): Description of what the item does
        on_use (callable, optional): Called when the item is used
        on_hit (callable, optional): Called when the holder is hit by a move
        on_switch_in (callable, optional): Called when the holder switches in
        on_after_move (callable, optional): Called after the holder uses a move
        on_before_move (callable, optional): Called before the holder uses a move
        on_faint (callable, optional): Called when the holder faints
        on_crit (callable, optional): Called when the holder lands a critical hit
        on_receive_crit (callable, optional): Called when the holder is hit by a critical hit
        on_status_apply (callable, optional): Called when the holder is inflicted with a status
        consumed (bool): Whether the item is consumed after use
    """
    name: str
    description: str
    on_use: Optional[Callable] = None
    on_hit: Optional[Callable] = None
    on_switch_in: Optional[Callable] = None
    on_after_move: Optional[Callable] = None
    on_before_move: Optional[Callable] = None
    on_faint: Optional[Callable] = None
    on_crit: Optional[Callable] = None
    on_receive_crit: Optional[Callable] = None
    on_status_apply: Optional[Callable] = None
    consumed: bool = False
    
    def use(self) -> bool:
        """Use the item.
        
        Returns:
            bool: True if the item was used successfully, False otherwise
        """
        if self.on_use:
            self.on_use()
            return self.consumed
        return False
    
    def __str__(self) -> str:
        """Return a string representation of the item."""
        return f"{self.name}: {self.description}"

# Common items
def create_item(name: str, description: str, consumed: bool = False, **kwargs) -> Item:
    """Helper function to create an item with the given callbacks.
    
    Args:
        name (str): Name of the item
        description (str): Description of the item
        consumed (bool): Whether the item is consumed after use
        **kwargs: Callback functions for the item
        
    Returns:
        Item: A new Item instance
    """
    return Item(name=name, description=description, consumed=consumed, **kwargs)

# Example items
LIFE_ORB = create_item(
    name="Life Orb",
    description="Powers up moves, but the holder loses 1/10 of its max HP after each move.",
    on_after_move=lambda battle, pokemon: battle.damage(pokemon, pokemon.max_hp // 10)
)

CHOICE_BAND = create_item(
    name="Choice Band",
    description="Boosts the power of physical moves by 50%, but restricts the user to one move.",
    on_before_move=lambda battle, pokemon, move: battle.boost_stat(pokemon, 'attack', 1) if move.category == 'Physical' else None
)

FOCUS_SASH = create_item(
    name="Focus Sash",
    description="If the holder has full HP and would be KO'd by an attack, it survives with 1 HP.",
    on_hit=lambda battle, target, move, damage: 1 if target.current_hp == target.max_hp and damage >= target.current_hp else damage,
    consumed=True
)

# Dictionary of all items
ITEMS = {
    'life_orb': LIFE_ORB,
    'choice_band': CHOICE_BAND,
    'focus_sash': FOCUS_SASH,
    # Add more items as needed
}

def get_item(name: str) -> Optional[Item]:
    """Get an item by name.
    
    Args:
        name (str): Name of the item (case-insensitive)
        
    Returns:
        Optional[Item]: The item if found, None otherwise
    """
    return ITEMS.get(name.lower().replace(' ', '_'))
