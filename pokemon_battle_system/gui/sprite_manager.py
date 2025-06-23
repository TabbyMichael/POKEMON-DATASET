"""
Sprite Manager for Pokémon Battle System

Handles loading and caching of Pokémon sprites from PokeAPI.
"""

import os
import pygame
import requests
from typing import Dict, Optional
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin

class SpriteManager:
    """Manages loading and caching of Pokémon sprites from PokeAPI."""
    
    BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    CACHE_DIR = Path("pokemon_sprites_cache")
    
    def __init__(self):
        """Initialize the sprite manager."""
        self.cache: Dict[str, pygame.Surface] = {}
        self._setup_cache_dir()
    
    def _setup_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        if not self.CACHE_DIR.exists():
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_pokemon_sprite(self, pokemon_name: str, sprite_type: str = "front_default") -> Optional[pygame.Surface]:
        """
        Get a Pokémon sprite from cache or download it.
        
        Args:
            pokemon_name: Name of the Pokémon (lowercase)
            sprite_type: Type of sprite to get (front_default, front_shiny, etc.)
            
        Returns:
            pygame.Surface with the sprite or None if loading failed
        """
        # Handle Pokémon with special names and forms
        pokemon_name = str(pokemon_name).lower()
        pokemon_name = pokemon_name.replace('♀', '-f')
        pokemon_name = pokemon_name.replace('♂', '-m')
        pokemon_name = pokemon_name.replace(' ', '-')
        pokemon_name = pokemon_name.replace('.', '')
        pokemon_name = pokemon_name.replace(':', '')
        
        # Special cases for Pokémon with different names in the API
        special_names = {
            'nidoranf': 'nidoran-f',
            'nidoranm': 'nidoran-m',
            'farfetchd': 'farfetchd',
            'mrmime': 'mr-mime',
            'mimejr': 'mime-jr',
            'typenull': 'type-null',
            'tapu-koko': 'tapu-koko',
            'tapu-lele': 'tapu-lele',
            'tapu-bulu': 'tapu-bulu',
            'tapu-fini': 'tapu-fini',
            'mr-rime': 'mr-rime',
            'sirfetchd': 'sirfetchd',
            'mr-mime-galar': 'mr-mime-galar',
            'mr-rime-galar': 'mr-rime-galar'
        }
        
        pokemon_name = special_names.get(pokemon_name, pokemon_name)
        cache_key = f"{pokemon_name}_{sprite_type}"
        
        # Return from cache if available
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load from cache file
        cache_file = self.CACHE_DIR / f"{cache_key}.png"
        if cache_file.exists():
            try:
                surface = pygame.image.load(str(cache_file))
                if surface.get_alpha():
                    surface = surface.convert_alpha()
                else:
                    surface = surface.convert()
                self.cache[cache_key] = surface
                return surface
            except pygame.error as e:
                print(f"Error loading cached sprite {cache_file}: {e}")
        
        # Download the sprite
        return self._download_pokemon_sprite(pokemon_name, sprite_type, cache_key, cache_file)
    
    def _download_pokemon_sprite(self, pokemon_name: str, sprite_type: str, 
                               cache_key: str, cache_file: Path) -> Optional[pygame.Surface]:
        """
        Download a Pokémon sprite from PokeAPI.
        
        Args:
            pokemon_name: Name of the Pokémon (lowercase)
            sprite_type: Type of sprite to get
            cache_key: Key to use for caching
            cache_file: Path to cache file
            
        Returns:
            pygame.Surface with the sprite or None if download failed
        """
        # Map sprite types to PokeAPI paths
        sprite_paths = {
            "front_default": f"sprites/pokemon/other/official-artwork/{pokemon_name}.png",
            "front_shiny": f"sprites/pokemon/other/official-artwork/shiny/{pokemon_name}.png",
            "back_default": f"sprites/pokemon/other/official-artwork/back/{pokemon_name}.png",
            "back_shiny": f"sprites/pokemon/other/official-artwork/back/shiny/{pokemon_name}.png",
        }
        
        if sprite_type not in sprite_paths:
            print(f"Unsupported sprite type: {sprite_type}")
            return None
            
        url = urljoin(self.BASE_URL, sprite_paths[sprite_type])
        print(f"Downloading sprite from {url}")
        
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Load image data into pygame
            image_data = BytesIO(response.content)
            surface = pygame.image.load(image_data)
            
            # Convert to optimal format
            if surface.get_alpha():
                surface = surface.convert_alpha()
            else:
                surface = surface.convert()
            
            # Cache the surface
            self.cache[cache_key] = surface
            
            # Save to cache file
            try:
                pygame.image.save(surface, str(cache_file))
            except Exception as e:
                print(f"Error saving sprite to cache {cache_file}: {e}")
            
            return surface
            
        except requests.RequestException as e:
            print(f"Failed to download sprite {url}: {e}")
            return None
        except pygame.error as e:
            print(f"Failed to load image data from {url}: {e}")
            return None
    
    def scale_sprite(self, sprite: pygame.Surface, max_size: int) -> pygame.Surface:
        """
        Scale a sprite to fit within a maximum size while maintaining aspect ratio.
        
        Args:
            sprite: The sprite to scale
            max_size: Maximum width/height of the scaled sprite
            
        Returns:
            Scaled pygame.Surface
        """
        if sprite is None:
            return None
            
        width, height = sprite.get_size()
        if width <= max_size and height <= max_size:
            return sprite
            
        ratio = min(max_size / width, max_size / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return pygame.transform.smoothscale(sprite, (new_width, new_height))
