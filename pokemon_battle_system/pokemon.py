"""Pokémon class for battle system."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
import random

from .enums import StatusCondition, VolatileStatus, MoveCategory
from .move import Move
from .ability import Ability
from .item import Item

@dataclass
class Pokemon:
    """Represents a Pokémon in battle.
    
    Attributes:
        name (str): The name of the Pokémon
        level (int): The level of the Pokémon (1-100)
        hp (int): Base HP stat
        attack (int): Base Attack stat
        defense (int): Base Defense stat
        special_attack (int): Base Special Attack stat
        special_defense (int): Base Special Defense stat
        speed (int): Base Speed stat
        primary_type (str): Primary type
        secondary_type (str, optional): Secondary type
        moves (List[Move]): List of known moves
        ability (Ability, optional): The Pokémon's ability
        item (Item, optional): The Pokémon's held item
        status (StatusCondition, optional): Current status condition
        volatile_status (Set[VolatileStatus]): Current volatile status conditions
        stat_stages (Dict[str, int]): Current stat stages (-6 to +6)
        current_hp (int): Current HP
        max_hp (int): Maximum HP (calculated from base stats and level)
    """
    name: str
    level: int = 50
    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0
    primary_type: str = ""
    secondary_type: str = ""
    moves: List[Move] = field(default_factory=list)
    ability: Optional[Ability] = None
    item: Optional[Item] = None
    status: Optional[StatusCondition] = StatusCondition.NONE
    volatile_status: Set[VolatileStatus] = field(default_factory=set)
    stat_stages: Dict[str, int] = field(default_factory=dict)
    current_hp: int = 0
    max_hp: int = 0
    
    def __post_init__(self):
        """Initialize calculated fields."""
        # Calculate max HP using standard formula: ((2 * base + IV + (EV/4)) * level / 100) + level + 10
        # For simplicity, we'll assume perfect IVs and no EVs for now
        self.max_hp = ((2 * self.hp) * self.level // 100) + self.level + 10
        self.current_hp = self.max_hp
        
        # Initialize stat stages
        self.stat_stages = {
            'attack': 0,
            'defense': 0,
            'special_attack': 0,
            'special_defense': 0,
            'speed': 0,
            'accuracy': 0,
            'evasion': 0
        }
    
    def get_stat(self, stat_name: str) -> int:
        """Get the current value of a stat, considering stat stages.
        
        Args:
            stat_name (str): Name of the stat ('hp', 'attack', 'defense', etc.)
            
        Returns:
            int: The current value of the stat
        """
        if stat_name == 'hp':
            return self.current_hp
            
        # Get base stat
        base_stat = getattr(self, stat_name, 0)
        
        # For HP, just return current HP
        if stat_name == 'hp':
            return self.current_hp
            
        # Calculate stat using standard formula: ((2 * base + IV + (EV/4)) * level / 100 + 5) * nature
        # For simplicity, we'll assume neutral nature and perfect IVs/EVs for now
        stat_value = ((2 * base_stat) * self.level // 100) + 5
        
        # Apply stat stages
        stage = self.stat_stages.get(stat_name, 0)
        if stage > 0:
            stat_value = stat_value * (2 + stage) // 2
        elif stage < 0:
            stat_value = stat_value * 2 // (2 - stage)
            
        return max(1, stat_value)  # Stats can't go below 1
    
    def take_damage(self, amount: int) -> None:
        """Reduce the Pokémon's HP by the given amount.
        
        Args:
            amount (int): Amount of damage to take
        """
        self.current_hp = max(0, min(self.current_hp - amount, self.max_hp))
    
    def heal(self, amount: int) -> int:
        """Heal the Pokémon by the given amount.
        
        Args:
            amount (int): Amount of HP to restore
            
        Returns:
            int: Actual amount healed
        """
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def is_fainted(self) -> bool:
        """Check if the Pokémon has fainted.
        
        Returns:
            bool: True if the Pokémon has fainted, False otherwise
        """
        return self.current_hp <= 0
    
    def has_type(self, type_name: str) -> bool:
        """Check if the Pokémon has a specific type.
        
        Args:
            type_name (str): Type to check for
            
        Returns:
            bool: True if the Pokémon has the type, False otherwise
        """
        return (self.primary_type.lower() == type_name.lower() or 
                (self.secondary_type and self.secondary_type.lower() == type_name.lower()))
    
    def get_types(self) -> List[str]:
        """Get a list of the Pokémon's types.
        
        Returns:
            List[str]: List of type names
        """
        types = [self.primary_type]
        if self.secondary_type:
            types.append(self.secondary_type)
        return types
    
    def add_volatile_status(self, status: VolatileStatus) -> bool:
        """Add a volatile status condition.
        
        Args:
            status (VolatileStatus): The status to add
            
        Returns:
            bool: True if the status was added, False if already had it
        """
        if status not in self.volatile_status:
            self.volatile_status.add(status)
            return True
        return False
    
    def remove_volatile_status(self, status: VolatileStatus) -> bool:
        """Remove a volatile status condition.
        
        Args:
            status (VolatileStatus): The status to remove
            
        Returns:
            bool: True if the status was removed, False if not present
        """
        if status in self.volatile_status:
            self.volatile_status.remove(status)
            return True
        return False
    
    def has_volatile_status(self, status: VolatileStatus) -> bool:
        """Check if the Pokémon has a specific volatile status.
        
        Args:
            status (VolatileStatus): The status to check for
            
        Returns:
            bool: True if the Pokémon has the status, False otherwise
        """
        return status in self.volatile_status
    
    def modify_stat_stage(self, stat: str, amount: int) -> int:
        """Modify a stat stage.
        
        Args:
            stat (str): Name of the stat to modify
            amount (int): Amount to change the stat stage by (can be negative)
            
        Returns:
            int: The new stat stage
        """
        if stat not in self.stat_stages:
            raise ValueError(f"Invalid stat: {stat}")
            
        new_stage = max(-6, min(6, self.stat_stages[stat] + amount))
        self.stat_stages[stat] = new_stage
        return new_stage
    
    def reset_stat_stages(self) -> None:
        """Reset all stat stages to 0."""
        for stat in self.stat_stages:
            self.stat_stages[stat] = 0
    
    def get_move(self, move_name: str) -> Optional[Move]:
        """Get a move by name.
        
        Args:
            move_name (str): Name of the move to get
            
        Returns:
            Optional[Move]: The move if found, None otherwise
        """
        for move in self.moves:
            if move.name.lower() == move_name.lower():
                return move
        return None
    
    def has_move(self, move_name: str) -> bool:
        """Check if the Pokémon has a specific move.
        
        Args:
            move_name (str): Name of the move to check for
            
        Returns:
            bool: True if the Pokémon has the move, False otherwise
        """
        return any(move.name.lower() == move_name.lower() for move in self.moves)
    
    def __str__(self) -> str:
        """Return a string representation of the Pokémon."""
        types = f"{self.primary_type}"
        if self.secondary_type:
            types += f"/{self.secondary_type}"
            
        status = f" ({self.status.value})" if self.status and self.status != StatusCondition.NONE else ""
        
        return (
            f"{self.name} ({types}) Lv.{self.level}\n"
            f"HP: {self.current_hp}/{self.max_hp} {self.get_hp_bar()}\n"
            f"ATK: {self.attack} | DEF: {self.defense} | SP.ATK: {self.special_attack} | "
            f"SP.DEF: {self.special_defense} | SPE: {self.speed}{status}"
        )
    
    def get_hp_bar(self, width: int = 20) -> str:
        """Get a visual representation of the Pokémon's HP.
        
        Args:
            width (int): Width of the HP bar in characters
            
        Returns:
            str: The HP bar as a string
        """
        if self.max_hp <= 0:
            return "[DEAD]"
            
        hp_percent = self.current_hp / self.max_hp
        filled = int(hp_percent * width)
        bar = '█' * filled + ' ' * (width - filled)
        
        if hp_percent > 0.5:
            color = "\033[92m"  # Green
        elif hp_percent > 0.2:
            color = "\033[93m"  # Yellow
        else:
            color = "\033[91m"  # Red
            
        return f"[{color}{bar}\033[0m] {self.current_hp}/{self.max_hp} ({hp_percent:.1%})"
