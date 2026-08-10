from src.games.chess import ChessBoard, ChessPiece
from src.games.chess.board import (
    square_index,
    square_row_col,
    algebraic_to_index,
    index_to_algebraic,
)


def test_square_index_a8_is_zero():
    assert square_index(0, 0) == 0


def test_square_index_h1_is_63():
    assert square_index(7, 7) == 63


def test_square_row_col_round_trip():
    for index in range(64):
        row, col = square_row_col(index)
        assert square_index(row, col) == index


def test_algebraic_round_trip():
    for algebraic in ["a8", "h1", "e4", "e5", "a1", "h8", "d7"]:
        assert index_to_algebraic(algebraic_to_index(algebraic)) == algebraic


def test_algebraic_to_index_known_squares():
    assert algebraic_to_index("a8") == 0
    assert algebraic_to_index("h8") == 7
    assert algebraic_to_index("a1") == 56
    assert algebraic_to_index("h1") == 63
    assert algebraic_to_index("e4") == square_index(4, 4)


def test_get_set_piece():
    board = ChessBoard([ChessPiece.EMPTY] * 64)
    board.set_piece(square_index(4, 4), ChessPiece.WHITE_QUEEN)

    assert board.get_piece(square_index(4, 4)) == ChessPiece.WHITE_QUEEN
    assert board.get_piece(0) == ChessPiece.EMPTY
