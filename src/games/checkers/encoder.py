import torch

from ...core.interfaces import GameState, StateEncoder, Move
from .board import CheckersPiece
from .state import CheckersPlayer


class CheckersEncoder(StateEncoder):
    @property
    def input_channels(self) -> int:
        return 5

    @property
    def action_size(self):
        return 1024

    def move_to_index(self, move: Move) -> int:
        # changes string moves to integer
        if '-' in move:
            parts = move.split('-')
        else:
            parts = move.split('x')
        start_idx = int(parts[0])
        final_idx = int(parts[-1])
        return start_idx * 32 + final_idx

    def encode(self, game_state: GameState) -> torch.Tensor:
        tensor = torch.zeros(1, 5, 8, 8, dtype=torch.float32)
        board = game_state.board
        for index in range(32):
            piece = board.get_piece(index)

            if piece is None or piece == CheckersPiece.EMPTY:
                continue
            row = index // 4
            if row % 2 == 0:
                col = (index % 4) * 2
            else:
                col = (index % 4) * 2 + 1
            if piece == CheckersPiece.WHITE:
                tensor[0, 0, row, col] = 1.0
            elif piece == CheckersPiece.WHITE_QUEEN:
                tensor[0, 1, row, col] = 1.0
            elif piece == CheckersPiece.BLACK:
                tensor[0, 2, row, col] = 1.0
            elif piece == CheckersPiece.BLACK_QUEEN:
                tensor[0, 3, row, col] = 1.0

        if game_state.active_player == CheckersPlayer.WHITE:
            tensor[0, 4, :, :] = 1.0
        else:
            tensor[0, 4, :, :] = 0.0

        return tensor
