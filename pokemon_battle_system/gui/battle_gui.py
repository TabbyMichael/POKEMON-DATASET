"""
Battle GUI for Pokémon battles using Pygame.

This module provides a graphical interface for the Pokémon battle system.
"""

import os
import sys
import pygame
import time
from typing import List, Tuple, Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import math
import random
from pathlib import Path

# Import sprite manager
from .sprite_manager import SpriteManager

# Import enums
from ..enums import MoveCategory

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
LIGHT_BLUE = (135, 206, 235)
DARK_GRAY = (100, 100, 100)
LIGHT_GRAY = (220, 220, 220)

# Animation states
class AnimationState(Enum):
    IDLE = "idle"
    ATTACK = "attack"
    DAMAGE = "damage"
    FAINT = "faint"
    SWITCH_IN = "switch_in"
    SWITCH_OUT = "switch_out"

@dataclass
class SpriteAnimation:
    """Class to handle sprite animations."""
    frames: List[pygame.Surface]
    frame_duration: float = 0.1
    loop: bool = True
    current_frame: int = 0
    frame_timer: float = 0
    done: bool = False
    
    def update(self, dt: float) -> None:
        """Update the animation."""
        if self.done:
            return
            
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.done = True
    
    def get_current_frame(self) -> pygame.Surface:
        """Get the current frame of the animation."""
        if not self.frames:
            return None
        return self.frames[self.current_frame]
    
    def reset(self) -> None:
        """Reset the animation to the beginning."""
        self.current_frame = 0
        self.frame_timer = 0
        self.done = False

class BattleGUI:
    """Main class for the battle GUI."""
    
    def __init__(self, battle):
        """Initialize the battle GUI.
        
        Args:
            battle: The Battle instance to visualize
        """
        self.battle = battle
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pokémon Battle")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Load assets
        self._load_assets()
        
        # UI elements
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_large = pygame.font.Font(None, 48)
        
        # Battle state
        self.message = ""
        self.message_timer = 0
        self.message_duration = 3.0  # seconds
        
        # Animation state
        self.animations = []
        
        # Set up Pokémon sprites
        self.player_pokemon_sprite = None
        self.opponent_pokemon_sprite = None
        self.setup_pokemon_sprites()
        
        # Battle menu
        self.menu_options = ["Fight", "Pokémon", "Bag", "Run"]
        self.selected_menu = 0
        self.show_move_menu = False
        self.move_menu_index = 0
        
        # Battle state
        self.waiting_for_input = True
    
    def _load_assets(self):
        """Load all required assets."""
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets"):
            os.makedirs("assets")
        
        # Load background
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(LIGHT_BLUE)  # Sky blue background
        
        # Load battle UI elements
        self.battle_ui = {
            'panel': pygame.Surface((SCREEN_WIDTH, 200)),
            'hp_bar': pygame.Surface((200, 20)),
            'hp_bar_fill': pygame.Surface((196, 16)),
            'menu': pygame.Surface((300, 150)),
            'menu_highlight': pygame.Surface((140, 60)),
        }
        
        # Style UI elements
        self.battle_ui['panel'].fill((230, 230, 230))
        self.battle_ui['menu'].fill((250, 250, 250))
        self.battle_ui['menu_highlight'].fill((200, 200, 255))
        
        # Draw borders
        pygame.draw.rect(self.battle_ui['panel'], DARK_GRAY, self.battle_ui['panel'].get_rect(), 2)
        pygame.draw.rect(self.battle_ui['menu'], DARK_GRAY, self.battle_ui['menu'].get_rect(), 2)
        pygame.draw.rect(self.battle_ui['menu_highlight'], BLUE, self.battle_ui['menu_highlight'].get_rect(), 2)
        
        # Initialize Pokémon sprites and battle state
        self.pokemon_sprites = {}
        if not hasattr(self, 'sprite_manager'):
            self.sprite_manager = SpriteManager()
            
        # Battle automation
        self.auto_battle = False
        self.auto_battle_delay = 1.0  # seconds between turns
        self.last_auto_action = 0
    
    def _load_pokemon_sprites(self):
        """Load or download Pokémon sprites."""
        if not hasattr(self, 'sprite_manager'):
            self.sprite_manager = SpriteManager()
            
        if self.player_pokemon_sprite and 'pokemon' in self.player_pokemon_sprite:
            pokemon = self.player_pokemon_sprite['pokemon']
            sprite = self.sprite_manager.get_pokemon_sprite(pokemon.name)
            if sprite:
                # Scale the sprite to a reasonable size
                scaled_sprite = self.sprite_manager.scale_sprite(sprite, 200)
                if scaled_sprite:
                    self.player_pokemon_sprite['sprite'] = scaled_sprite
                else:
                    self._create_placeholder_sprite(pokemon, is_player=True)
            else:
                self._create_placeholder_sprite(pokemon, is_player=True)
    
        if self.opponent_pokemon_sprite and 'pokemon' in self.opponent_pokemon_sprite:
            pokemon = self.opponent_pokemon_sprite['pokemon']
            sprite = self.sprite_manager.get_pokemon_sprite(pokemon.name)
            if sprite:
                # Scale the sprite to a reasonable size
                scaled_sprite = self.sprite_manager.scale_sprite(sprite, 200)
                if scaled_sprite:
                    self.opponent_pokemon_sprite['sprite'] = scaled_sprite
                else:
                    self._create_placeholder_sprite(pokemon, is_player=False)
            else:
                self._create_placeholder_sprite(pokemon, is_player=False)
    
    def _create_placeholder_sprite(self, pokemon, is_player=True):
        """Create a placeholder sprite if loading the real one fails."""
        sprite = pygame.Surface((120, 120), pygame.SRCALPHA)
        color = (100, 200, 100) if is_player else (200, 100, 100)
        pygame.draw.rect(sprite, color, (0, 0, 120, 120), border_radius=10)
        
        # Add Pokémon name
        font = pygame.font.Font(None, 20)
        text = font.render(pokemon.name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(60, 60))
        sprite.blit(text, text_rect)
        
        if is_player:
            self.player_pokemon_sprite['sprite'] = sprite
        else:
            self.opponent_pokemon_sprite['sprite'] = sprite
    
    def setup_pokemon_sprites(self):
        """Set up Pokémon sprites for the battle."""
        # Initialize sprite manager if not already done
        if not hasattr(self, 'sprite_manager'):
            self.sprite_manager = SpriteManager()
        
        # Find the first non-fainted Pokémon on each team
        for pokemon in self.battle.team1:
            if not pokemon.is_fainted():
                self.player_pokemon_sprite = {
                    'pokemon': pokemon,
                    'position': (200, 300),
                    'state': AnimationState.IDLE,
                    'sprite': None,  # Will be loaded by _load_pokemon_sprites
                    'anim_timer': 0,
                    'offset_x': 0,
                    'offset_y': 0,
                    'scale': 1.0,
                    'alpha': 255
                }
                break
                
        for pokemon in self.battle.team2:
            if not pokemon.is_fainted():
                self.opponent_pokemon_sprite = {
                    'pokemon': pokemon,
                    'position': (600, 150),
                    'state': AnimationState.IDLE,
                    'sprite': None,  # Will be loaded by _load_pokemon_sprites
                    'anim_timer': 0,
                    'offset_x': 0,
                    'offset_y': 0,
                    'scale': 1.0,
                    'alpha': 255
                }
                break
        
        # Load the sprites
        self._load_pokemon_sprites()
    
    def run(self):
        """Run the main game loop."""
        last_time = time.time()
        
        while self.running:
            # Calculate delta time
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            self._handle_events()
            
            # Update game state
            self._update(dt)
            
            # Draw everything
            self._draw()
            
            # Cap the frame rate
            self.clock.tick(FPS)
            
            # Update the display
            pygame.display.flip()
    
    def _handle_events(self):
        """Handle pygame events."""
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == pygame.USEREVENT and self.auto_battle:
                # Auto-battle: Make a random move for the player
                if not self.show_move_menu and not self.waiting_for_input:
                    self._auto_battle_move()
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop the timer
    
    def _handle_keydown(self, key):
        """Handle key press events."""
        if not self.waiting_for_input:
            return
            
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self._handle_confirm()
        elif key == pygame.K_UP:
            self._navigate_menu(0, -1)
        elif key == pygame.K_DOWN:
            self._navigate_menu(0, 1)
        elif key == pygame.K_LEFT:
            self._navigate_menu(-1, 0)
        elif key == pygame.K_RIGHT:
            self._navigate_menu(1, 0)
    
    def _navigate_menu(self, dx, dy):
        """Navigate the battle menu."""
        if self.show_move_menu:
            # In move selection
            self.move_menu_index = (self.move_menu_index + dx + dy * 2) % 4
        else:
            # In main menu
            if dx != 0:
                self.selected_menu = (self.selected_menu + (1 if dx > 0 else -1)) % 4
            if dy != 0:
                self.selected_menu = (self.selected_menu + (2 if dy > 0 else -2)) % 4
    
    def _handle_confirm(self):
        """Handle confirm button press."""
        if self.show_move_menu:
            # Select a move
            pokemon = self.player_pokemon_sprite['pokemon']
            if 0 <= self.move_menu_index < len(pokemon.moves):
                selected_move = pokemon.moves[self.move_menu_index]
                self.message = f"{pokemon.name} used {selected_move.name}!"
                self.show_move_menu = False
                self.waiting_for_input = False
                
                # Execute the move
                self._execute_move(pokemon, selected_move, self.opponent_pokemon_sprite['pokemon'])
                
                # Auto-battle: Let the opponent make a move
                if self.auto_battle and not self.opponent_pokemon_sprite['pokemon'].is_fainted():
                    pygame.time.set_timer(pygame.USEREVENT, int(self.auto_battle_delay * 1000))
        else:
            # Main menu selection
            if self.selected_menu == 0:  # Fight
                if self.player_pokemon_sprite['pokemon'].moves:
                    self.show_move_menu = True
                    self.move_menu_index = 0
                else:
                    self.message = "No moves available!"
            elif self.selected_menu == 1:  # Pokémon
                self.message = "Pokémon menu selected"
            elif self.selected_menu == 2:  # Bag
                self.message = "Bag menu selected"
            elif self.selected_menu == 3:  # Run/Toggle Auto-battle
                self.auto_battle = not self.auto_battle
                status = "enabled" if self.auto_battle else "disabled"
                self.message = f"Auto-battle {status}!"
                if self.auto_battle and not self.show_move_menu:
                    pygame.time.set_timer(pygame.USEREVENT, int(self.auto_battle_delay * 1000))
    
    def _update(self, dt):
        """Update game state."""
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""
                self.waiting_for_input = True
        
        # Update Pokémon animations
        self._update_pokemon_animation(dt, self.player_pokemon_sprite)
        self._update_pokemon_animation(dt, self.opponent_pokemon_sprite)
    
    def _update_pokemon_animation(self, dt, pokemon_sprite):
        """Update a Pokémon's animation."""
        if not pokemon_sprite:
            return
            
        pokemon_sprite['anim_timer'] += dt
        
        # Handle different animation states
        if pokemon_sprite['state'] == AnimationState.IDLE:
            # Gentle bobbing animation
            pokemon_sprite['offset_y'] = math.sin(pokemon_sprite['anim_timer'] * 2) * 2
        elif pokemon_sprite['state'] == AnimationState.ATTACK:
            # Attack animation (move forward and back)
            if pokemon_sprite['anim_timer'] < 0.1:
                pokemon_sprite['offset_x'] = 30 if pokemon_sprite == self.player_pokemon_sprite else -30
            elif pokemon_sprite['anim_timer'] < 0.2:
                pokemon_sprite['offset_x'] = 0
                pokemon_sprite['state'] = AnimationState.IDLE
        elif pokemon_sprite['state'] == AnimationState.DAMAGE:
            # Damage animation (flash red)
            if pokemon_sprite['anim_timer'] < 0.6:
                if int(pokemon_sprite['anim_timer'] * 10) % 2 == 0:
                    pokemon_sprite['alpha'] = 100
                else:
                    pokemon_sprite['alpha'] = 255
            else:
                pokemon_sprite['alpha'] = 255
                pokemon_sprite['state'] = AnimationState.IDLE
    
    def _draw(self):
        """Draw everything to the screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw battle UI panel
        self.screen.blit(self.battle_ui['panel'], (0, SCREEN_HEIGHT - 200))
        
        # Draw auto-battle indicator
        if self.auto_battle:
            font = pygame.font.Font(None, 24)
            auto_text = font.render("AUTO", True, (255, 0, 0))
            self.screen.blit(auto_text, (SCREEN_WIDTH - 60, 10))
        
        # Draw Pokémon sprites
        self._draw_pokemon(self.player_pokemon_sprite)
        self._draw_pokemon(self.opponent_pokemon_sprite)
        
        # Draw message box
        self._draw_message_box()
        
        # Draw battle menu
        if self.waiting_for_input:
            if self.show_move_menu:
                self._draw_move_menu()
            else:
                self._draw_main_menu()
    
    def _draw_pokemon(self, pokemon_sprite):
        """Draw a Pokémon sprite with its current animation state."""
        if not pokemon_sprite or not pokemon_sprite['sprite']:
            return
            
        # Create a copy of the sprite to apply transformations
        sprite = pokemon_sprite['sprite'].copy()
        
        # Apply alpha if needed
        if pokemon_sprite['alpha'] < 255:
            sprite.fill((255, 255, 255, pokemon_sprite['alpha']), None, pygame.BLEND_RGBA_MULT)
        
        # Apply scale if needed
        if pokemon_sprite['scale'] != 1.0:
            new_width = int(sprite.get_width() * pokemon_sprite['scale'])
            new_height = int(sprite.get_height() * pokemon_sprite['scale'])
            sprite = pygame.transform.scale(sprite, (new_width, new_height))
        
        # Get position with offset
        x = pokemon_sprite['position'][0] + pokemon_sprite['offset_x']
        y = pokemon_sprite['position'][1] + pokemon_sprite['offset_y']
        
        # Draw the sprite
        self.screen.blit(sprite, (x - sprite.get_width() // 2, y - sprite.get_height() // 2))
        
        # Draw HP bar if applicable
        if pokemon_sprite == self.player_pokemon_sprite:
            self._draw_hp_bar(pokemon_sprite, 50, SCREEN_HEIGHT - 180)
        else:
            self._draw_hp_bar(pokemon_sprite, SCREEN_WIDTH - 250, 50)
    
    def _draw_hp_bar(self, pokemon_sprite, x, y):
        """Draw an HP bar for a Pokémon."""
        if not pokemon_sprite:
            return
            
        pokemon = pokemon_sprite['pokemon']
        hp_percent = pokemon.current_hp / pokemon.max_hp
        
        # Draw HP bar background
        pygame.draw.rect(self.screen, DARK_GRAY, (x, y, 200, 20))
        
        # Determine HP bar color
        if hp_percent > 0.5:
            color = GREEN
        elif hp_percent > 0.2:
            color = YELLOW
        else:
            color = RED
        
        # Draw HP bar fill
        bar_width = int(196 * hp_percent)
        pygame.draw.rect(self.screen, color, (x + 2, y + 2, bar_width, 16))
        
        # Draw HP text
        hp_text = f"HP: {pokemon.current_hp}/{pokemon.max_hp}"
        text_surface = self.font_small.render(hp_text, True, BLACK)
        self.screen.blit(text_surface, (x + 10, y + 25))
        
        # Draw Pokémon name and level
        name_text = f"{pokemon.name} Lv.{pokemon.level}"
        name_surface = self.font_medium.render(name_text, True, BLACK)
        self.screen.blit(name_surface, (x, y - 30))
    
    def _draw_message_box(self):
        """Draw the message box with the current message."""
        if not self.message:
            return
            
        # Draw message box background
        pygame.draw.rect(self.screen, WHITE, (20, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 40, 100))
        pygame.draw.rect(self.screen, BLACK, (20, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 40, 100), 2)
        
        # Draw message text with word wrapping
        words = self.message.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font_medium.render(test_line, True, BLACK)
            if test_surface.get_width() < SCREEN_WIDTH - 80:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line of text
        for i, line in enumerate(lines):
            text_surface = self.font_medium.render(line, True, BLACK)
            self.screen.blit(text_surface, (40, SCREEN_HEIGHT - 150 + i * 30))
    
    def _draw_main_menu(self):
        """Draw the main battle menu."""
        menu_x = SCREEN_WIDTH - 320
        menu_y = SCREEN_HEIGHT - 160
        
        # Draw menu background
        self.screen.blit(self.battle_ui['menu'], (menu_x, menu_y))
        
        # Draw menu options
        for i, option in enumerate(self.menu_options):
            x = menu_x + 20 + (i % 2) * 140
            y = menu_y + 20 + (i // 2) * 60
            
            # Highlight selected option
            if i == self.selected_menu:
                self.screen.blit(self.battle_ui['menu_highlight'], (x - 10, y - 10))
            
            # Draw option text
            text_surface = self.font_medium.render(option, True, BLACK)
            self.screen.blit(text_surface, (x, y))
    
    def _draw_move_menu(self):
        """Draw the move selection menu."""
        if not self.player_pokemon_sprite or 'pokemon' not in self.player_pokemon_sprite:
            return
            
        pokemon = self.player_pokemon_sprite['pokemon']
        if not hasattr(pokemon, 'moves') or not pokemon.moves:
            return
            
        menu_x = 20
        menu_y = SCREEN_HEIGHT - 180
        menu_width = SCREEN_WIDTH - 40
        menu_height = 150
        
        # Draw menu background
        pygame.draw.rect(self.screen, WHITE, (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 2)
        
        # Draw move list
        pokemon = self.player_pokemon_sprite['pokemon']
        for i, move in enumerate(pokemon.moves):
            if i >= 4:  # Only show 4 moves max
                break
                
            row = i // 2
            col = i % 2
            x = menu_x + 20 + col * (menu_width // 2)
            y = menu_y + 20 + row * 60
            
            # Highlight selected move
            if i == self.move_menu_index:
                pygame.draw.rect(self.screen, (200, 200, 255), (x - 10, y - 10, 360, 50))
            
            # Draw move name and PP
            move_text = f"{move.name}"
            pp_text = f"PP {move.pp}/{move.max_pp}"
            
            move_surface = self.font_medium.render(move_text, True, BLACK)
            pp_surface = self.font_small.render(pp_text, True, DARK_GRAY)
            
            self.screen.blit(move_surface, (x, y))
            self.screen.blit(pp_surface, (x, y + 30))
    
    def show_message(self, message: str, duration: float = 3.0):
        """Display a message in the battle UI.
        
        Args:
            message: The message to display
            duration: How long to show the message in seconds
        """
        self.message = message
        self.message_timer = duration
        self.waiting_for_input = False
    
    def _execute_move(self, attacker, move, defender):
        """Execute a move in battle."""
        # Animate the attack
        self.animate_attack(attacker, defender)
        
        # Calculate damage (simplified for now)
        damage = 0
        if move.power > 0:
            # Simple damage calculation (can be enhanced with actual formulas)
            attack = attacker.attack if move.category == MoveCategory.PHYSICAL else attacker.special_attack
            defense = defender.defense if move.category == MoveCategory.PHYSICAL else defender.special_defense
            damage = max(1, int((attacker.level * 0.4 + 2) * attack * move.power / (defense * 50) + 2))
        
        # Apply damage
        defender.current_hp = max(0, defender.current_hp - damage)
        self.message = f"{attacker.name} used {move.name}! It dealt {damage} damage!"
        
        # Check for fainting
        if defender.is_fainted():
            self.message = f"{defender.name} fainted!"
            if defender == self.player_pokemon_sprite['pokemon']:
                self.player_pokemon_sprite['state'] = AnimationState.FAINT
            else:
                self.opponent_pokemon_sprite['state'] = AnimationState.FAINT
    
    def _auto_battle_move(self):
        """Make a random move for auto-battle."""
        if not self.waiting_for_input and not self.show_move_menu:
            # Player's turn
            if self.player_pokemon_sprite and not self.player_pokemon_sprite['pokemon'].is_fainted():
                pokemon = self.player_pokemon_sprite['pokemon']
                if pokemon.moves:
                    move = random.choice(pokemon.moves)
                    self.message = f"{pokemon.name} used {move.name}!"
                    self._execute_move(pokemon, move, self.opponent_pokemon_sprite['pokemon'])
            
            # Opponent's turn (if still alive)
            if (self.opponent_pokemon_sprite and 
                not self.opponent_pokemon_sprite['pokemon'].is_fainted() and
                not self.player_pokemon_sprite['pokemon'].is_fainted()):
                pokemon = self.opponent_pokemon_sprite['pokemon']
                if pokemon.moves:
                    move = random.choice(pokemon.moves)
                    self.message = f"Opponent's {pokemon.name} used {move.name}!"
                    self._execute_move(pokemon, move, self.player_pokemon_sprite['pokemon'])
    
    def animate_attack(self, attacker, defender):
        """Animate a Pokémon attack."""
        if self.player_pokemon_sprite and 'pokemon' in self.player_pokemon_sprite:
            if attacker == self.player_pokemon_sprite['pokemon']:
                self.player_pokemon_sprite['state'] = AnimationState.ATTACK
                self.player_pokemon_sprite['anim_timer'] = 0
            elif defender == self.player_pokemon_sprite['pokemon']:
                self.player_pokemon_sprite['state'] = AnimationState.DAMAGE
                self.player_pokemon_sprite['anim_timer'] = 0
        
        if self.opponent_pokemon_sprite and 'pokemon' in self.opponent_pokemon_sprite:
            if attacker == self.opponent_pokemon_sprite['pokemon']:
                self.opponent_pokemon_sprite['state'] = AnimationState.ATTACK
                self.opponent_pokemon_sprite['anim_timer'] = 0
            elif defender == self.opponent_pokemon_sprite['pokemon']:
                self.opponent_pokemon_sprite['state'] = AnimationState.DAMAGE
                self.opponent_pokemon_sprite['anim_timer'] = 0

class BattleGUIWrapper:
    """Wrapper class to integrate with the existing battle system."""
    
    def __init__(self, battle):
        """Initialize the battle GUI wrapper.
        
        Args:
            battle: The Battle instance to visualize
        """
        self.battle = battle
        self.gui = BattleGUI(battle)
    
    def start(self):
        """Start the battle GUI."""
        self.gui.show_message("A wild battle has started!")
        self.gui.run()

if __name__ == "__main__":
    # Example usage
    from ..battle import create_sample_battle
    
    battle = create_sample_battle()
    gui = BattleGUIWrapper(battle)
    gui.start()
