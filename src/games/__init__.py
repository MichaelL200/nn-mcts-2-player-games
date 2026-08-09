from .checkers import Checkers, CheckersPlayer, CheckersUI, CheckersEncoder  # noqa

GAMES = {
    "checkers": {
        "simulation": Checkers,
        "ui": CheckersUI,
        "model_file": "checkers_alphazero_model.pt",
    },
}
