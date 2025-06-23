"""Pokémon Battle System

A comprehensive battle system for Pokémon battles with support for:
- Turn-based battles
- Abilities and held items
- Weather and terrain effects
- Status conditions and stat changes
- Team preview and switching
"""

# Import core components
from .enums import (
    MoveCategory, Weather, Terrain, 
    SideCondition, StatusCondition, VolatileStatus
)
from .move import Move
from .pokemon import Pokemon
from .ability import Ability, create_ability, get_ability
from .item import Item, create_item, get_item
from .battle import Battle, create_sample_battle

__all__ = [
    # Core classes
    'Pokemon', 'Move', 'Ability', 'Item', 'Battle',
    
    # Enums
    'MoveCategory', 'Weather', 'Terrain', 
    'SideCondition', 'StatusCondition', 'VolatileStatus',
    
    # Factory functions
    'create_ability', 'get_ability',
    'create_item', 'get_item',
    'create_sample_battle'
]
