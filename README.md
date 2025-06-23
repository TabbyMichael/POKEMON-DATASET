# Pokémon Battle Simulator

A Python-based Pokémon battle simulator with a Pygame GUI that supports turn-based battles, type effectiveness, and move execution.

## Project Structure

```
Pokemon-Dataset/
├── data/                    # Data files (CSVs, etc.)
├── output/                  # Generated output files (images, etc.)
├── pokemon_battle_system/   # Core battle system implementation
│   ├── gui/                 # GUI components
│   ├── __init__.py
│   ├── ability.py
│   ├── battle.py
│   ├── enums.py
│   ├── item.py
│   ├── move.py
│   ├── pokemon.py
│   └── trainer.py
├── assets/                  # Static assets (images, sounds)
├── gui_battle_demo.py       # Main demo script
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Features

- Turn-based Pokémon battles
- Support for multiple Pokémon per trainer
- Type effectiveness calculations
- Move execution with accuracy and critical hits
- Simple Pygame-based GUI
- Auto-battle mode

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the demo:
   ```
   python gui_battle_demo.py
   ```

## Controls

- Arrow keys: Navigate menus
- Z/Enter: Confirm selection
- X: Go back
- R: Toggle auto-battle mode

## Dependencies

- Python 3.8+
- Pygame
- colorama
- requests

## License

MIT
# POKEMON-DATASET
