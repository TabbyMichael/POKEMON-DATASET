"""Move class for Pokémon battle system."""
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from .enums import MoveCategory

@dataclass
class Move:
    """Represents a move that a Pokémon can use in battle.
    
    Attributes:
        name (str): The name of the move
        type (str): The type of the move (e.g., 'Fire', 'Water')
        power (int): Base power of the move (0 for status moves)
        accuracy (int): Accuracy of the move (0-100)
        pp (int): Current PP of the move
        max_pp (int): Maximum PP of the move
        category (MoveCategory): Physical, Special, or Status
        priority (int): Move priority (higher goes first)
        effect (dict, optional): Additional effects of the move
        target (str): Target of the move ('normal', 'self', 'allAdjacentFoes', etc.)
        flags (Dict[str, bool]): Additional flags for the move
    """
    name: str
    type: str
    power: int
    accuracy: int
    pp: int
    max_pp: int
    category: MoveCategory
    priority: int = 0
    effect: Optional[dict] = None
    target: str = "normal"
    flags: Dict[str, bool] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the move with default values."""
        if self.pp > self.max_pp:
            self.pp = self.max_pp
    
    def use(self) -> bool:
        """Use the move, consuming PP.
        
        Returns:
            bool: True if the move was used successfully, False if out of PP
        """
        if self.pp > 0:
            self.pp -= 1
            return True
        return False
    
    def restore_pp(self, amount: int = None) -> None:
        """Restore PP to the move.
        
        Args:
            amount (int, optional): Amount of PP to restore. If None, restores to max.
        """
        if amount is None:
            self.pp = self.max_pp
        else:
            self.pp = min(self.max_pp, self.pp + amount)
    
    def get_effectiveness(self, target_types: List[str]) -> float:
        """Calculate the effectiveness of this move against target types.
        
        Args:
            target_types (List[str]): The types of the target Pokémon
            
        Returns:
            float: Effectiveness multiplier (0, 0.25, 0.5, 1, 2, or 4)
        """
        # This would be implemented with the type chart
        # For now, return neutral damage
        return 1.0
    
    def is_super_effective(self, target_types: List[str]) -> bool:
        """Check if the move is super effective against the target types."""
        return self.get_effectiveness(target_types) > 1.0
    
    def is_not_very_effective(self, target_types: List[str]) -> bool:
        """Check if the move is not very effective against the target types."""
        return 0 < self.get_effectiveness(target_types) < 1.0
    
    def has_no_effect(self, target_types: List[str]) -> bool:
        """Check if the move has no effect on the target types."""
        return self.get_effectiveness(target_types) == 0
    
    def get_stab_multiplier(self, user_types: List[str]) -> float:
        """Calculate the STAB (Same Type Attack Bonus) multiplier.
        
        Args:
            user_types (List[str]): The types of the using Pokémon
            
        Returns:
            float: 1.5 if the move matches one of the user's types, 1.0 otherwise
        """
        return 1.5 if self.type.lower() in [t.lower() for t in user_types] else 1.0
    
    def __str__(self) -> str:
        """Return a string representation of the move."""
        return f"{self.name} ({self.type}, {self.power} power, {self.accuracy}% acc, {self.pp}/{self.max_pp} PP)"
