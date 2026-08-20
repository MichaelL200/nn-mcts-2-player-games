from .checkers import Checkers, CheckersPlayer, CheckersUI, CheckersEncoder  # noqa
from .chess import Chess, ChessPlayer, ChessEncoder, ChessUI  # noqa

GAMES = {
    "checkers": {
        "simulation": Checkers,
        "ui": CheckersUI,
        "model_file": "checkers_alphazero_model.pt",
    },
    "chess": {
        "simulation": Chess,
        "ui": ChessUI,
        "model_file": "chess_alphazero_model.pt",
    },
}
