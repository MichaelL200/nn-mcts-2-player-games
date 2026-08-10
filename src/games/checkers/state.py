from enum import Enum
from .board import CheckersBoard
from ...core.interfaces import GameState


class CheckersPlayer(Enum):
    WHITE = 1
    BLACK = -1


class CheckersState(GameState):
    def __init__(
        self,
        board: CheckersBoard,
        active_player: CheckersPlayer,
        moves_without_progress: int = 0,
        reduced_material_moves: int = 0,
        reduced_material_key: tuple | None = None,
        position_history: dict | None = None,
    ):
        super().__init__(board, active_player)
        self.moves_without_progress = moves_without_progress
        self.reduced_material_moves = reduced_material_moves
        self.reduced_material_key = reduced_material_key
        self.position_history = position_history if position_history is not None else {}

    def get_player(self) -> CheckersPlayer:
        return self.active_player

    def get_board(self) -> CheckersBoard:
        return self.board
