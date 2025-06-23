"""
Pokémon Battle Simulator with GUI

This script demonstrates the Pokémon battle system with a graphical user interface.
"""
import os
import sys
import random
import pygame
from colorama import init, Fore, Style

# Local imports
from pokemon_battle_system.battle import Battle
from pokemon_battle_system.trainer import Trainer
from pokemon_battle_system.pokemon import Pokemon
from pokemon_battle_system.move import Move, MoveCategory
from pokemon_battle_system.gui.battle_gui import BattleGUI

# Initialize colorama
init()

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize colorama for console output
init()

# Import the battle system
from pokemon_battle_system.gui.battle_gui import BattleGUIWrapper
from pokemon_battle_system.battle import Battle, Pokemon, Move
from pokemon_battle_system.trainer import Trainer
from pokemon_battle_system.enums import MoveCategory

def create_sample_pokemon():
    """Create sample Pokémon with moves for the demo."""
    # Create moves with categories
    moves = [
        Move(name="Tackle", type="Normal", power=40, accuracy=100, pp=35, max_pp=35, category=MoveCategory.PHYSICAL),
        Move(name="Ember", type="Fire", power=40, accuracy=100, pp=25, max_pp=25, category=MoveCategory.SPECIAL),
        Move(name="Water Gun", type="Water", power=40, accuracy=100, pp=25, max_pp=25, category=MoveCategory.SPECIAL),
        Move(name="Vine Whip", type="Grass", power=45, accuracy=100, pp=25, max_pp=25, category=MoveCategory.PHYSICAL),
        Move(name="Thunderbolt", type="Electric", power=90, accuracy=100, pp=15, max_pp=15, category=MoveCategory.SPECIAL),
        Move(name="Ice Beam", type="Ice", power=90, accuracy=100, pp=10, max_pp=10, category=MoveCategory.SPECIAL),
        Move(name="Earthquake", type="Ground", power=100, accuracy=100, pp=10, max_pp=10, category=MoveCategory.PHYSICAL),
        Move(name="Psychic", type="Psychic", power=90, accuracy=100, pp=10, max_pp=10, category=MoveCategory.SPECIAL),
        Move(name="Flamethrower", type="Fire", power=90, accuracy=100, pp=15, max_pp=15, category=MoveCategory.SPECIAL),
        Move(name="Surf", type="Water", power=90, accuracy=100, pp=15, max_pp=15, category=MoveCategory.SPECIAL),
        Move(name="Solar Beam", type="Grass", power=120, accuracy=100, pp=10, max_pp=10, category=MoveCategory.SPECIAL),
        Move(name="Thunder", type="Electric", power=110, accuracy=70, pp=10, max_pp=10, category=MoveCategory.SPECIAL)
    ]
    
    # Create Pokémon with stats and moves
    pokemon_list = [
        {"name": "Pikachu", "type1": "Electric", "type2": None, 
         "hp": 35, "atk": 55, "def": 40, "sp_atk": 50, "sp_def": 50, "speed": 90,
         "moves": ["Thunderbolt", "Quick Attack", "Iron Tail", "Thunder"]},
        {"name": "Charizard", "type1": "Fire", "type2": "Flying",
         "hp": 78, "atk": 84, "def": 78, "sp_atk": 109, "sp_def": 85, "speed": 100,
         "moves": ["Flamethrower", "Air Slash", "Dragon Claw", "Solar Beam"]},
        {"name": "Blastoise", "type1": "Water", "type2": None,
         "hp": 79, "atk": 83, "def": 100, "sp_atk": 85, "sp_def": 105, "speed": 78,
         "moves": ["Surf", "Ice Beam", "Flash Cannon", "Earthquake"]},
        {"name": "Venusaur", "type1": "Grass", "type2": "Poison",
         "hp": 80, "atk": 82, "def": 83, "sp_atk": 100, "sp_def": 100, "speed": 80,
         "moves": ["Solar Beam", "Sludge Bomb", "Earthquake", "Synthesis"]},
        {"name": "Gengar", "type1": "Ghost", "type2": "Poison",
         "hp": 60, "atk": 65, "def": 60, "sp_atk": 130, "sp_def": 75, "speed": 110,
         "moves": ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Psychic"]},
        {"name": "Dragonite", "type1": "Dragon", "type2": "Flying",
         "hp": 91, "atk": 134, "def": 95, "sp_atk": 100, "sp_def": 100, "speed": 80,
         "moves": ["Outrage", "Hurricane", "Fire Blast", "Thunder"]}
    ]
    
    # Create Pokémon objects with random moves
    pokemon_objects = []
    for pkmn in random.sample(pokemon_list, 3):  # Pick 3 random Pokémon
        # Find the move objects
        pkmn_moves = []
        for move_name in pkmn["moves"]:
            move = next((m for m in moves if m.name == move_name), None)
            if move:
                pkmn_moves.append(move)
        
        # Add some random moves if needed
        while len(pkmn_moves) < 4 and moves:
            move = random.choice(moves)
            if move not in pkmn_moves:
                pkmn_moves.append(move)
        
        # Create the Pokémon with proper initialization
        pokemon = Pokemon(
            name=pkmn["name"],
            level=50,  # Level 50 for better stats
            primary_type=pkmn["type1"],
            secondary_type=pkmn["type2"] or "",
            hp=pkmn["hp"],
            attack=pkmn["atk"],
            defense=pkmn["def"],
            special_attack=pkmn["sp_atk"],
            special_defense=pkmn["sp_def"],
            speed=pkmn["speed"]
        )
        # Set current HP to max HP
        pokemon.current_hp = pokemon.hp
        pokemon.moves = pkmn_moves
        pokemon_objects.append(pokemon)
    
    return pokemon_objects

def main():
    print(f"{Fore.CYAN}=== Pokémon Battle Simulator with GUI ==={Style.RESET_ALL}\n")
    
    # Initialize pygame and set up display
    pygame.init()
    pygame.display.set_caption("Pokémon Battle Simulator")
    
    print("Creating battle...")
    
    # Create Pokémon for player and opponent
    player_pokemon = create_sample_pokemon()
    opponent_pokemon = create_sample_pokemon()
    
    # Create trainers
    player = Trainer("Ash")
    for pkmn in player_pokemon:
        player.add_pokemon(pkmn)
    
    opponent = Trainer("Gary")
    for pkmn in opponent_pokemon:
        opponent.add_pokemon(pkmn)
    
    # Create battle with the teams
    battle = Battle(player.party, opponent.party)
    
    print(f"Battle started: {player.name} vs {opponent.name}")
    print("Controls:")
    print("- Arrow keys to navigate")
    print("- Z/Enter to confirm")
    print("- X to go back")
    print("- Press 'Run' to toggle auto-battle")
    
    # Create and run GUI
    try:
        gui = BattleGUIWrapper(battle)
        gui.start()
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up pygame
        pygame.quit()

if __name__ == "__main__":
    main()
