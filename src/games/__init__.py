from .checkers import Checkers, CheckersPlayer, CheckersUI, CheckersEncoder  # noqa
from .chess import Chess, ChessPlayer, ChessEncoder  # noqa

GAMES = {
    "checkers": {
        "simulation": Checkers,
        "ui": CheckersUI,
        "model_file": "checkers_alphazero_model.pt",
    },
    "chess": {
        "simulation": Chess,
        "ui": None,
        "model_file": "chess_alphazero_model.pt",
    },
}
