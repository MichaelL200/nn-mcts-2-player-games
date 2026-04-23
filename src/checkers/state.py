from enum import Enum
from .board import CheckersBoard
from ..core import GameState


class CheckersPlayer(Enum):
    WHITE = 1
    BLACK = -1


class CheckersState(GameState):
    def __init__(self, board: CheckersBoard, active_player: CheckersPlayer):
        self.board = board
        self.active_player = active_player

    def get_player(self) -> CheckersPlayer:
        return self.active_player

    def get_board(self) -> CheckersBoard:
        return self.board
