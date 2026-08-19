import torch

from ...core.interfaces import StateEncoder, Move
from .board import ChessPiece, square_row_col
from .state import ChessState, ChessPlayer
from .game_logic import parse_move

_PIECE_PLANE = {
    ChessPiece.WHITE_PAWN: 0,
    ChessPiece.WHITE_KNIGHT: 1,
    ChessPiece.WHITE_BISHOP: 2,
    ChessPiece.WHITE_ROOK: 3,
    ChessPiece.WHITE_QUEEN: 4,
    ChessPiece.WHITE_KING: 5,
    ChessPiece.BLACK_PAWN: 6,
    ChessPiece.BLACK_KNIGHT: 7,
    ChessPiece.BLACK_BISHOP: 8,
    ChessPiece.BLACK_ROOK: 9,
    ChessPiece.BLACK_QUEEN: 10,
    ChessPiece.BLACK_KING: 11,
}

_SIDE_TO_MOVE_PLANE = 12
_CASTLE_WHITE_KINGSIDE_PLANE = 13
_CASTLE_WHITE_QUEENSIDE_PLANE = 14
_CASTLE_BLACK_KINGSIDE_PLANE = 15
_CASTLE_BLACK_QUEENSIDE_PLANE = 16
_EN_PASSANT_PLANE = 17
_HALFMOVE_CLOCK_PLANE = 18

_UNDERPROMOTION_PIECE_INDEX = {"n": 0, "b": 1, "r": 2}  # 'q' - queen is the default handled by regular move encoding


class ChessEncoder(StateEncoder):
    @property
    def input_channels(self) -> int:
        return 19

    @property
    def action_size(self) -> int:
        return 4240

    def move_to_index(self, move: Move) -> int:
        from_square, to_square, promotion = parse_move(move)
        if promotion is None or promotion == "q":
            return from_square * 64 + to_square
        return 4096 + _underpromotion_offset(from_square, to_square, promotion)

    def encode(self, game_state: ChessState) -> torch.Tensor:
        tensor = torch.zeros(1, 19, 8, 8, dtype=torch.float32)
        board = game_state.board

        for index, piece in enumerate(board.squares):
            if piece == ChessPiece.EMPTY:
                continue
            row, col = square_row_col(index)
            tensor[0, _PIECE_PLANE[piece], row, col] = 1.0

        if game_state.active_player == ChessPlayer.WHITE:
            tensor[0, _SIDE_TO_MOVE_PLANE, :, :] = 1.0

        if game_state.castle_white_kingside:
            tensor[0, _CASTLE_WHITE_KINGSIDE_PLANE, :, :] = 1.0
        if game_state.castle_white_queenside:
            tensor[0, _CASTLE_WHITE_QUEENSIDE_PLANE, :, :] = 1.0
        if game_state.castle_black_kingside:
            tensor[0, _CASTLE_BLACK_KINGSIDE_PLANE, :, :] = 1.0
        if game_state.castle_black_queenside:
            tensor[0, _CASTLE_BLACK_QUEENSIDE_PLANE, :, :] = 1.0

        if game_state.en_passant is not None:
            row, col = square_row_col(game_state.en_passant)
            tensor[0, _EN_PASSANT_PLANE, row, col] = 1.0

        tensor[0, _HALFMOVE_CLOCK_PLANE, :, :] = game_state.halfmove_clock / 100.0

        return tensor


def _underpromotion_offset(from_square: int, to_square: int, promotion: str) -> int:
    from_row, from_col = square_row_col(from_square)
    _, to_col = square_row_col(to_square)
    color = 0 if from_row == 1 else 1  # White pawn promotes after moving from row 1
    # Map from_col - 1 (capture-left), from_col (push), or from_col + 1 (capture-right) to 0, 1, 2
    direction = to_col - from_col + 1
    return color * 72 + from_col * 9 + direction * 3 + _UNDERPROMOTION_PIECE_INDEX[promotion]
