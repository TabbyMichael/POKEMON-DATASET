"""Trainer class for Pokémon battle system."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .pokemon import Pokemon

@dataclass
class Trainer:
    """Represents a Pokémon trainer.
    
    Attributes:
        name (str): Trainer's name
        party (List[Pokemon]): List of Pokémon in the trainer's party
        current_pokemon (Optional[Pokemon]): Currently active Pokémon
        items (Dict[str, int]): Items the trainer has
        battle_stats (Dict[str, Any]): Battle statistics
    """
    name: str
    party: List[Pokemon] = field(default_factory=list)
    current_pokemon: Optional[Pokemon] = None
    items: Dict[str, int] = field(default_factory=dict)
    battle_stats: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the trainer's current Pokémon."""
        if self.party and self.current_pokemon is None:
            self.current_pokemon = self.party[0]
    
    def switch_pokemon(self, index: int) -> bool:
        """
        Switch to a different Pokémon.
        
        Args:
            index: Index of the Pokémon to switch to
            
        Returns:
            bool: True if the switch was successful, False otherwise
        """
        if 0 <= index < len(self.party):
            if self.party[index].current_hp > 0:  # Can't switch to fainted Pokémon
                self.current_pokemon = self.party[index]
                return True
        return False
    
    def has_usable_pokemon(self) -> bool:
        """
        Check if the trainer has any usable Pokémon left.
        
        Returns:
            bool: True if there's at least one non-fainted Pokémon
        """
        return any(pokemon.current_hp > 0 for pokemon in self.party)
    
    def get_available_pokemon(self) -> List[Pokemon]:
        """
        Get a list of non-fainted Pokémon that aren't currently in battle.
        
        Returns:
            List[Pokemon]: List of available Pokémon
        """
        return [
            pokemon for pokemon in self.party 
            if pokemon.current_hp > 0 and pokemon != self.current_pokemon
        ]
    
    def add_pokemon(self, pokemon: Pokemon) -> None:
        """
        Add a Pokémon to the trainer's party.
        
        Args:
            pokemon: Pokémon to add
        """
        if len(self.party) < 6:  # Maximum party size is 6
            self.party.append(pokemon)
            if self.current_pokemon is None:
                self.current_pokemon = pokemon
    
    def remove_pokemon(self, pokemon: Pokemon) -> bool:
        """
        Remove a Pokémon from the trainer's party.
        
        Args:
            pokemon: Pokémon to remove
            
        Returns:
            bool: True if the Pokémon was removed, False otherwise
        """
        if pokemon in self.party:
            self.party.remove(pokemon)
            if self.current_pokemon == pokemon:
                self.current_pokemon = self.party[0] if self.party else None
            return True
        return False
