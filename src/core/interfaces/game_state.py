from typing import TypeAlias
from abc import ABC


Move: TypeAlias = str


class Board(ABC):
    pass


class Player(ABC):
    pass


class GameState(ABC):
    def __init__(self, board: Board, active_player: Player):
        self.board = board
        self.active_player = active_player
