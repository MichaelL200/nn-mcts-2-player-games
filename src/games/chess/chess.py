import numpy as np

from ...core.interfaces import GameSimulation, Move
from .state import ChessState, ChessPlayer, enemy_color
from .encoder import ChessEncoder
from .game_logic import (
    generate_legal_moves,
    advance,
    is_checkmate,
    is_stalemate,
    is_draw_by_fifty_move_rule,
    is_draw_by_repetition,
    has_insufficient_material,
)

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class Chess(GameSimulation):
    def __init__(self):
        self._encoder = ChessEncoder()

    @property
    def encoder(self) -> ChessEncoder:
        return self._encoder

    def get_starting_state(self) -> ChessState:
        return ChessState.from_fen(STARTING_FEN)

    def get_moves(self, game_state: ChessState) -> list[Move]:
        return generate_legal_moves(game_state)

    def make_move(self, game_state: ChessState, move: Move) -> ChessState:
        return advance(game_state, move)

    def make_random_move(self, game_state: ChessState) -> ChessState:
        random_move = np.random.choice(self.get_moves(game_state))
        return self.make_move(game_state, random_move)

    def is_terminal(self, game_state: ChessState) -> bool:
        # Source for possible draws https://en.wikipedia.org/wiki/Draw_(chess)
        return (
            is_checkmate(game_state)
            or is_stalemate(game_state)
            or is_draw_by_fifty_move_rule(game_state)
            or is_draw_by_repetition(game_state)
            or has_insufficient_material(game_state.board)
        )

    def reward(self, game_state: ChessState, desired_winner: ChessPlayer) -> int | None:
        if not self.is_terminal(game_state):
            return None
        if is_checkmate(game_state):
            winner = enemy_color(game_state.active_player)
            return 1 if winner == desired_winner else -1
        return 0
