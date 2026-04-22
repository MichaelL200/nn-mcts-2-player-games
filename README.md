
# KNSI GOLEM MCTS Checkers [![Flake8 Linting](https://github.com/KNSI-Golem/monte-carlo-checkers/actions/workflows/lint.yaml/badge.svg)](https://github.com/KNSI-Golem/monte-carlo-checkers/actions/workflows/lint.yaml) [![Pytest](https://github.com/KNSI-Golem/monte-carlo-checkers/actions/workflows/test.yaml/badge.svg)](https://github.com/KNSI-Golem/monte-carlo-checkers/actions/workflows/test.yaml)

This repository contains implementation of MCTS search algorithm along with orginal checkers made from scratch. It was prepared as a part of 2025's Konik stand for KNSI Golem to provide some form of attraction.

### Code and Files Structure
To ensure a transparent and easily understandable file structure for external users each module, from making plots to training models, is given its respective file in the `src` folder. A full description of the file structure is provided in the [Project Organization](#project-organization) section.

**How to run code in repository?**
Use our packaged modules that strike your interest by importing them to your file of choice. (This repo contains already prepared 'main.py' as a demo)
- Install requirements:
```bash
python3 -m venv .venv  # Create venv  
source .venv/bin/activate  # Activate venv  
pip install -r requirements.txt  # Install requirements to venv  
pre-commit install  # Setup git hooks for linting
```
- Run code:
```bash
python3 train.py  # Train neural network model (default 10 iterations might take a while)
python3 main.py   # Run demo (falls back to random rollouts if no model found)
```

## Project Organization

```
├── README.md          <- The top-level README for developers using this project.
│
├── docs               <- Project's docs (currently none)
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8 and pytest
│
├── main.py            <- Try your luck with our MCTS firsthand
│
└── src                <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes src a Python module
    │
    │── checkers                <- Checkers implemention
    │
    │   ├── __init__.py 
    │   ├── board.py            <- Board object           
    │   ├── checkers.py         <- Main rules, no data stored
    │   └── state.py            <- State providing info about current turn
    │
    │── interfaces              <- Templates for strctures accepted by our MCTS 
    │
    │   ├── __init__.py 
    │   ├── game_simulation.py  <- Gamesimulation providing just rules
    │   └── game_state.py       <- Move, Board, Player and Gamestate
    │
    │── mcts                    <- MCTS algorithm prepared for checkers and other games
    │
    │   ├── __init__.py 
    │   ├── mcts_node.py        <- Single node of a tree never to be used on its own     
    │   └── mcts_tree.py        <- Main algorithm for searching through given gamespace
    │
    │── gui                     <- Pygame wrapper around checkers game
    │
    │   ├── __init__.py 
    │   ├── game.py             <- Code to run interactive game instance          
    │   └── display.py          <- Code to draw checkers board
    │
    └── other                   <- Leftover files from earlier stages
```

## Credits
- ['mrserji'](https://mrserji.itch.io/) for their checkers assets 
