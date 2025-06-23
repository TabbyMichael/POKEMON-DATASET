"""Battle class for Pokémon battle system."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set, Any, Union
import random
import time
from colorama import Fore, Style, Back

from .enums import (
    MoveCategory, Weather, Terrain, SideCondition, StatusCondition, VolatileStatus
)
from .pokemon import Pokemon
from .move import Move
from .ability import Ability
from .item import Item

class Battle:
    """Represents a Pokémon battle between two trainers.
    
    Attributes:
        team1 (List[Pokemon]): First trainer's team
        team2 (List[Pokemon]): Second trainer's team
        weather (Weather): Current weather condition
        terrain (Terrain): Current terrain
        turn (int): Current turn number
        sides (Dict[str, Dict]): Information about each side of the field
        log (List[str]): Battle log
    """
    
    def __init__(self, team1: List[Pokemon], team2: List[Pokemon]):
        """Initialize a new battle.
        
        Args:
            team1 (List[Pokemon]): First trainer's team
            team2 (List[Pokemon]): Second trainer's team
        """
        self.team1 = team1
        self.team2 = team2
        self.weather = Weather.CLEAR
        self.terrain = Terrain.NONE
        self.turn = 0
        self.sides = {
            'p1': {'conditions': set(), 'reflect': 0, 'light_screen': 0, 'aurora_veil': 0},
            'p2': {'conditions': set(), 'reflect': 0, 'light_screen': 0, 'aurora_veil': 0}
        }
        self.log = []
        self._init_teams()
    
    def _init_teams(self) -> None:
        """Initialize the teams for battle."""
        for pokemon in self.team1 + self.team2:
            # Set up initial HP and stat stages
            pokemon.current_hp = pokemon.max_hp
            pokemon.reset_stat_stages()
            
            # Reset status conditions (except for fainted Pokémon)
            if pokemon.status == StatusCondition.FAINTED:
                pokemon.status = StatusCondition.NONE
    
    def start_battle(self) -> None:
        """Start the battle."""
        self.log_message("The battle has begun!")
        self._show_team_preview()
        self._begin_battle()
    
    def _show_team_preview(self) -> None:
        """Show a preview of both teams."""
        self.log_message("\n=== TEAM PREVIEW ===")
        
        self.log_message("\nTeam 1:")
        for i, pokemon in enumerate(self.team1, 1):
            types = f"{pokemon.primary_type}"
            if pokemon.secondary_type:
                types += f"/{pokemon.secondary_type}"
            self.log_message(f"{i}. {pokemon.name} ({types}) - Lv. {pokemon.level}")
        
        self.log_message("\nTeam 2:")
        for i, pokemon in enumerate(self.team2, 1):
            types = f"{pokemon.primary_type}"
            if pokemon.secondary_type:
                types += f"/{pokemon.secondary_type}"
            self.log_message(f"{i}. {pokemon.name} ({types}) - Lv. {pokemon.level}")
        
        self.log_message("\nThe battle will begin shortly...")
        time.sleep(2)
    
    def _begin_battle(self) -> None:
        """Begin the main battle loop."""
        # Start with first Pokémon in each team
        active_p1 = self.team1[0]
        active_p2 = self.team2[0]
        
        self.log_message(f"\n{Fore.BLUE}Team 1 sends out {active_p1.name}!{Style.RESET_ALL}")
        self.log_message(f"{Fore.RED}Team 2 sends out {active_p2.name}!{Style.RESET_ALL}")
        
        # Main battle loop
        while not self._is_battle_over():
            self.turn += 1
            self.log_message(f"\n{Fore.CYAN}=== Turn {self.turn} ==={Style.RESET_ALL}")
            
            # Check for weather and terrain effects
            self._handle_weather_effects()
            self._handle_terrain_effects()
            
            # Get moves for both Pokémon
            move_p1 = self._select_move(active_p1, active_p2)
            move_p2 = self._select_move(active_p2, active_p1)
            
            # Determine move order
            first, second = self._determine_move_order(active_p1, move_p1, active_p2, move_p2)
            
            # Execute moves
            self._execute_move(*first)
            if not self._is_battle_over():
                self._execute_move(*second)
            
            # End of turn effects
            self._end_of_turn_effects(active_p1, active_p2)
            
            # Check for fainted Pokémon
            if active_p1.is_fainted():
                self.log_message(f"\n{active_p1.name} fainted!")
                active_p1 = self._select_replacement(active_p1, self.team1, "Team 1")
                if not active_p1:
                    break
            
            if active_p2.is_fainted():
                self.log_message(f"\n{active_p2.name} fainted!")
                active_p2 = self._select_replacement(active_p2, self.team2, "Team 2")
                if not active_p2:
                    break
        
        # Battle ended
        self._end_battle()
    
    def _select_move(self, attacker: Pokemon, defender: Pokemon) -> Move:
        """Select a move for a Pokémon to use.
        
        Args:
            attacker (Pokemon): The attacking Pokémon
            defender (Pokemon): The defending Pokémon
            
        Returns:
            Move: The selected move
        """
        # Simple AI: Choose the move with the highest damage output
        best_move = None
        max_damage = 0
        
        for move in attacker.moves:
            if move.pp <= 0:
                continue
                
            # Calculate expected damage
            damage = self._calculate_damage(attacker, defender, move)
            
            # Consider type effectiveness
            effectiveness = self._calculate_type_effectiveness(move, defender)
            damage *= effectiveness
            
            # Consider STAB
            if move.type.lower() in [t.lower() for t in attacker.get_types()]:
                damage *= 1.5
            
            if damage > max_damage:
                max_damage = damage
                best_move = move
        
        # If no moves left, use Struggle
        if not best_move:
            return Move("Struggle", "Normal", 50, 100, -1, -1, MoveCategory.PHYSICAL)
        
        return best_move
    
    def _calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move) -> float:
        """Calculate the damage of a move.
        
        Args:
            attacker (Pokemon): The attacking Pokémon
            defender (Pokemon): The defending Pokémon
            move (Move): The move being used
            
        Returns:
            float: The calculated damage
        """
        if move.category == MoveCategory.STATUS:
            return 0
            
        # Base damage calculation
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.get_stat('attack')
            defense = defender.get_stat('defense')
        else:  # Special
            attack = attacker.get_stat('special_attack')
            defense = defender.get_stat('special_defense')
        
        # Base damage formula
        damage = ((2 * attacker.level / 5 + 2) * move.power * attack / defense) / 50 + 2
        
        # Apply STAB
        if move.type.lower() in [t.lower() for t in attacker.get_types()]:
            damage *= 1.5
        
        # Apply type effectiveness
        effectiveness = self._calculate_type_effectiveness(move, defender)
        damage *= effectiveness
        
        # Apply critical hit (4.17% chance, or 12.5% with high crit moves)
        if random.random() < (0.125 if move.flags.get('high_crit', False) else 0.0417):
            damage *= 1.5
            self.log_message("A critical hit!")
        
        # Apply random factor (0.85 to 1.0)
        damage *= random.uniform(0.85, 1.0)
        
        return max(1, damage)
    
    def _calculate_type_effectiveness(self, move: Move, defender: Pokemon) -> float:
        """Calculate type effectiveness of a move against a Pokémon.
        
        Args:
            move (Move): The move being used
            defender (Pokemon): The defending Pokémon
            
        Returns:
            float: Effectiveness multiplier (0, 0.25, 0.5, 1, 2, or 4)
        """
        # This is a simplified type chart - in a real implementation, you'd want a complete one
        type_chart = {
            'normal': {'rock': 0.5, 'ghost': 0, 'steel': 0.5},
            'fire': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 2, 'bug': 2, 'rock': 0.5, 'dragon': 0.5, 'steel': 2},
            'water': {'fire': 2, 'water': 0.5, 'grass': 0.5, 'ground': 2, 'rock': 2, 'dragon': 0.5},
            'electric': {'water': 2, 'electric': 0.5, 'grass': 0.5, 'ground': 0, 'flying': 2, 'dragon': 0.5},
            'grass': {'fire': 0.5, 'water': 2, 'grass': 0.5, 'poison': 0.5, 'ground': 2, 'flying': 0.5, 'bug': 0.5, 'rock': 2, 'dragon': 0.5, 'steel': 0.5},
            'ice': {'fire': 0.5, 'water': 0.5, 'grass': 2, 'ice': 0.5, 'ground': 2, 'flying': 2, 'dragon': 2, 'steel': 0.5},
            'fighting': {'normal': 2, 'ice': 2, 'poison': 0.5, 'flying': 0.5, 'psychic': 0.5, 'bug': 0.5, 'rock': 2, 'ghost': 0, 'dark': 2, 'steel': 2, 'fairy': 0.5},
            'poison': {'grass': 2, 'poison': 0.5, 'ground': 0.5, 'rock': 0.5, 'ghost': 0.5, 'steel': 0, 'fairy': 2},
            'ground': {'fire': 2, 'electric': 2, 'grass': 0.5, 'poison': 2, 'flying': 0, 'bug': 0.5, 'rock': 2, 'steel': 2},
            'flying': {'electric': 0.5, 'grass': 2, 'fighting': 2, 'bug': 2, 'rock': 0.5, 'steel': 0.5},
            'psychic': {'fighting': 2, 'poison': 2, 'psychic': 0.5, 'dark': 0, 'steel': 0.5},
            'bug': {'fire': 0.5, 'grass': 2, 'fighting': 0.5, 'poison': 0.5, 'flying': 0.5, 'psychic': 2, 'ghost': 0.5, 'dark': 2, 'steel': 0.5, 'fairy': 0.5},
            'rock': {'fire': 2, 'ice': 2, 'fighting': 0.5, 'ground': 0.5, 'flying': 2, 'bug': 2, 'steel': 0.5},
            'ghost': {'normal': 0, 'psychic': 2, 'ghost': 2, 'dark': 0.5},
            'dragon': {'dragon': 2, 'steel': 0.5, 'fairy': 0},
            'dark': {'fighting': 0.5, 'psychic': 2, 'ghost': 2, 'dark': 0.5, 'fairy': 0.5},
            'steel': {'fire': 0.5, 'water': 0.5, 'electric': 0.5, 'ice': 2, 'rock': 2, 'steel': 0.5, 'fairy': 2},
            'fairy': {'fire': 0.5, 'fighting': 2, 'poison': 0.5, 'dragon': 2, 'dark': 2, 'steel': 0.5}
        }
        
        effectiveness = 1.0
        move_type = move.type.lower()
        
        # Check against primary type
        if move_type in type_chart and defender.primary_type.lower() in type_chart[move_type]:
            effectiveness *= type_chart[move_type][defender.primary_type.lower()]
        
        # Check against secondary type
        if defender.secondary_type and defender.secondary_type.lower() in type_chart.get(move_type, {}):
            effectiveness *= type_chart[move_type][defender.secondary_type.lower()]
        
        # Log effectiveness
        if effectiveness == 0:
            self.log_message("It doesn't affect " + defender.name + "...")
        elif effectiveness < 1:
            self.log_message("It's not very effective...")
        elif effectiveness > 1:
            self.log_message("It's super effective!")
        
        return effectiveness
    
    def _determine_move_order(self, p1: Pokemon, move1: Move, p2: Pokemon, move2: Move) -> Tuple:
        """Determine the order of moves based on priority and speed.
        
        Args:
            p1 (Pokemon): First Pokémon
            move1 (Move): First Pokémon's move
            p2 (Pokemon): Second Pokémon
            move2 (Move): Second Pokémon's move
            
        Returns:
            Tuple: (first_pokemon, first_move, second_pokemon), (second_pokemon, second_move, first_pokemon)
        """
        # Compare move priorities
        if move1.priority > move2.priority:
            return (p1, move1, p2), (p2, move2, p1)
        elif move2.priority > move1.priority:
            return (p2, move2, p1), (p1, move1, p2)
        
        # Same priority, compare speed
        p1_speed = p1.get_stat('speed')
        p2_speed = p2.get_stat('speed')
        
        # Apply paralysis speed drop
        if p1.status == StatusCondition.PARALYSIS:
            p1_speed = int(p1_speed * 0.5)
        if p2.status == StatusCondition.PARALYSIS:
            p2_speed = int(p2_speed * 0.5)
        
        # Check for speed ties
        if p1_speed == p2_speed:
            # Randomly decide in case of tie
            if random.random() < 0.5:
                return (p1, move1, p2), (p2, move2, p1)
            else:
                return (p2, move2, p1), (p1, move1, p2)
        elif p1_speed > p2_speed:
            return (p1, move1, p2), (p2, move2, p1)
        else:
            return (p2, move2, p1), (p1, move1, p2)
    
    def _execute_move(self, attacker: Pokemon, move: Move, defender: Pokemon) -> None:
        """Execute a move in battle.
        
        Args:
            attacker (Pokemon): The attacking Pokémon
            move (Move): The move to use
            defender (Pokemon): The defending Pokémon
        """
        if attacker.is_fainted() or defender.is_fainted():
            return
            
        self.log_message(f"{Fore.CYAN}{attacker.name}{Style.RESET_ALL} used {Fore.YELLOW}{move.name}{Style.RESET_ALL}!")
        
        # Check for accuracy
        accuracy_check = random.random() * 100
        if accuracy_check > move.accuracy:
            self.log_message("But it missed!")
            return
        
        # Handle status moves
        if move.category == MoveCategory.STATUS:
            self._handle_status_move(attacker, move, defender)
            return
        
        # Calculate damage
        damage = int(self._calculate_damage(attacker, defender, move))
        
        # Apply damage
        defender.take_damage(damage)
        
        # Log damage
        self.log_message(f"{defender.name} took {damage} damage!")
        self.log_message(defender.get_hp_bar())
        
        # Apply move effects
        if move.effect:
            self._apply_move_effects(attacker, defender, move)
        
        # Check for fainting
        if defender.is_fainted():
            self.log_message(f"{defender.name} fainted!")
    
    def _handle_status_move(self, user: Pokemon, move: Move, target: Pokemon) -> None:
        """Handle a status move.
        
        Args:
            user (Pokemon): The Pokémon using the move
            move (Move): The status move
            target (Pokemon): The target of the move
        """
        self.log_message(f"{user.name} used {move.name}!")
        
        # Apply move effects
        if move.effect:
            self._apply_move_effects(user, target, move)
    
    def _apply_move_effects(self, user: Pokemon, target: Pokemon, move: Move) -> None:
        """Apply the effects of a move.
        
        Args:
            user (Pokemon): The Pokémon using the move
            target (Pokemon): The target of the move
            move (Move): The move being used
        """
        if not move.effect:
            return
            
        effect = move.effect
        
        # Stat changes
        if 'stat' in effect and random.random() < effect.get('chance', 1.0):
            stat = effect['stat']
            stages = effect['stages']
            target.modify_stat_stage(stat, stages)
            
            # Determine if stat was raised or lowered
            if stages > 0:
                self.log_message(f"{target.name}'s {stat} rose!")
            else:
                self.log_message(f"{target.name}'s {stat} fell!")
        
        # Status conditions
        if 'status' in effect and random.random() < effect.get('chance', 1.0):
            status = StatusCondition(effect['status'])
            self._apply_status_condition(target, status)
    
    def _apply_status_condition(self, target: Pokemon, status: StatusCondition) -> None:
        """Apply a status condition to a Pokémon.
        
        Args:
            target (Pokemon): The Pokémon to apply the status to
            status (StatusCondition): The status condition to apply
        """
        if target.status == StatusCondition.NONE:
            target.status = status
            self.log_message(f"{target.name} was {status.value}ed!")
    
    def _handle_weather_effects(self) -> None:
        """Handle weather effects at the end of the turn."""
        if self.weather == Weather.SANDSTORM:
            self.log_message("The sandstorm rages!")
            # Apply damage to non-Rock, Ground, or Steel types
            # ...
        elif self.weather == Weather.HAIL:
            self.log_message("The hail continues to fall!")
            # Apply damage to non-Ice types
            # ...
    
    def _handle_terrain_effects(self) -> None:
        """Handle terrain effects."""
        if self.terrain != Terrain.NONE:
            self.log_message(f"The {self.terrain.value} continues to affect the battlefield!")
    
    def _end_of_turn_effects(self, p1: Pokemon, p2: Pokemon) -> None:
        """Handle end of turn effects like status damage and weather."""
        # Handle status conditions
        for pokemon in [p1, p2]:
            if pokemon.status == StatusCondition.BURN:
                damage = max(1, pokemon.max_hp // 8)
                pokemon.take_damage(damage)
                self.log_message(f"{pokemon.name} was hurt by its burn!")
            elif pokemon.status == StatusCondition.POISON:
                damage = max(1, pokemon.max_hp // 8)
                pokemon.take_damage(damage)
                self.log_message(f"{pokemon.name} was hurt by poison!")
            elif pokemon.status == StatusCondition.TOXIC:
                # Toxic poison increases each turn
                if 'toxic_counter' not in pokemon.volatile_status:
                    pokemon.volatile_status.add('toxic_counter')
                    pokemon.toxic_counter = 1
                else:
                    pokemon.toxic_counter += 1
                damage = max(1, (pokemon.max_hp * pokemon.toxic_counter) // 16)
                pokemon.take_damage(damage)
                self.log_message(f"{pokemon.name} was hurt by toxic!")
        
        # Decrease weather turns
        # ...
    
    def _is_battle_over(self) -> bool:
        """Check if the battle is over.
        
        Returns:
            bool: True if the battle is over, False otherwise
        """
        team1_alive = any(not pokemon.is_fainted() for pokemon in self.team1)
        team2_alive = any(not pokemon.is_fainted() for pokemon in self.team2)
        return not (team1_alive and team2_alive)
    
    def _select_replacement(self, fainted: Pokemon, team: List[Pokemon], team_name: str) -> Optional[Pokemon]:
        """Select a replacement for a fainted Pokémon.
        
        Args:
            fainted (Pokemon): The fainted Pokémon
            team (List[Pokemon]): The team to select from
            team_name (str): Name of the team (for display)
            
        Returns:
            Optional[Pokemon]: The selected Pokémon, or None if no valid choices
        """
        available = [p for p in team if not p.is_fainted() and p != fainted]
        if not available:
            return None
        
        # Simple AI: Choose the Pokémon with the highest HP
        return max(available, key=lambda p: p.hp)
    
    def _end_battle(self) -> None:
        """Handle the end of the battle."""
        team1_alive = any(not pokemon.is_fainted() for pokemon in self.team1)
        team2_alive = any(not pokemon.is_fainted() for pokemon in self.team2)
        
        if team1_alive and not team2_alive:
            self.log_message("\nTeam 1 wins the battle!")
        elif team2_alive and not team1_alive:
            self.log_message("\nTeam 2 wins the battle!")
        else:
            self.log_message("\nThe battle ended in a draw!")
    
    def log_message(self, message: str) -> None:
        """Log a battle message.
        
        Args:
            message (str): The message to log
        """
        print(message)
        self.log.append(message)

def create_sample_battle() -> Battle:
    """Create a sample battle for testing.
    
    Returns:
        Battle: A sample battle
    """
    from .move import Move
    from .pokemon import Pokemon
    from .ability import ABILITIES
    from .item import ITEMS
    
    # Create moves
    flamethrower = Move(
        name="Flamethrower",
        type="Fire",
        power=90,
        accuracy=100,
        pp=15,
        max_pp=15,
        category=MoveCategory.SPECIAL,
        effect={'status': 'burn', 'chance': 0.1}
    )
    
    thunderbolt = Move(
        name="Thunderbolt",
        type="Electric",
        power=90,
        accuracy=100,
        pp=15,
        max_pp=15,
        category=MoveCategory.SPECIAL,
        effect={'status': 'paralysis', 'chance': 0.1}
    )
    
    ice_beam = Move(
        name="Ice Beam",
        type="Ice",
        power=90,
        accuracy=100,
        pp=10,
        max_pp=10,
        category=MoveCategory.SPECIAL,
        effect={'status': 'freeze', 'chance': 0.1}
    )
    
    earthquake = Move(
        name="Earthquake",
        type="Ground",
        power=100,
        accuracy=100,
        pp=10,
        max_pp=10,
        category=MoveCategory.PHYSICAL
    )
    
    close_combat = Move(
        name="Close Combat",
        type="Fighting",
        power=120,
        accuracy=100,
        pp=5,
        max_pp=5,
        category=MoveCategory.PHYSICAL,
        effect={
            'self_stat': 'defense',
            'stages': -1,
            'self_stat2': 'special_defense',
            'stages2': -1
        }
    )
    
    swords_dance = Move(
        name="Swords Dance",
        type="Normal",
        power=0,
        accuracy=100,
        pp=20,
        max_pp=20,
        category=MoveCategory.STATUS,
        effect={'self_stat': 'attack', 'stages': 2}
    )
    
    # Create Pokémon
    charizard = Pokemon(
        name="Charizard",
        level=50,
        hp=78,
        attack=84,
        defense=78,
        special_attack=109,
        special_defense=85,
        speed=100,
        primary_type="Fire",
        secondary_type="Flying",
        moves=[flamethrower, earthquake, swords_dance, Move(
            name="Air Slash",
            type="Flying",
            power=75,
            accuracy=95,
            pp=15,
            max_pp=15,
            category=MoveCategory.SPECIAL,
            effect={'flinch': 0.3}
        )]
    )
    
    blastoise = Pokemon(
        name="Blastoise",
        level=50,
        hp=79,
        attack=83,
        defense=100,
        special_attack=85,
        special_defense=105,
        speed=78,
        primary_type="Water",
        moves=[Move(
            name="Hydro Pump",
            type="Water",
            power=110,
            accuracy=80,
            pp=5,
            max_pp=5,
            category=MoveCategory.SPECIAL
        ), ice_beam, earthquake, Move(
            name="Flash Cannon",
            type="Steel",
            power=80,
            accuracy=100,
            pp=10,
            max_pp=10,
            category=MoveCategory.SPECIAL,
            effect={'stat': 'special_defense', 'stages': -1, 'chance': 0.1}
        )]
    )
    
    venusaur = Pokemon(
        name="Venusaur",
        level=50,
        hp=80,
        attack=82,
        defense=83,
        special_attack=100,
        special_defense=100,
        speed=80,
        primary_type="Grass",
        secondary_type="Poison",
        moves=[Move(
            name="Solar Beam",
            type="Grass",
            power=120,
            accuracy=100,
            pp=10,
            max_pp=10,
            category=MoveCategory.SPECIAL
        ), Move(
            name="Sludge Bomb",
            type="Poison",
            power=90,
            accuracy=100,
            pp=10,
            max_pp=10,
            category=MoveCategory.SPECIAL,
            effect={'status': 'poison', 'chance': 0.3}
        ), earthquake, Move(
            name="Synthesis",
            type="Grass",
            power=0,
            accuracy=100,
            pp=5,
            max_pp=5,
            category=MoveCategory.STATUS,
            effect={'heal': 0.5}
        )]
    )
    
    # Create teams and battle
    team1 = [charizard, blastoise]
    team2 = [venusaur]
    
    return Battle(team1, team2)
