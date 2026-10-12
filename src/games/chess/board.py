from enum import IntEnum
from ...core.interfaces import Board


class ChessPiece(IntEnum):
    EMPTY = 0
    WHITE_PAWN = 1
    WHITE_KNIGHT = 2
    WHITE_BISHOP = 3
    WHITE_ROOK = 4
    WHITE_QUEEN = 5
    WHITE_KING = 6
    BLACK_PAWN = -1
    BLACK_KNIGHT = -2
    BLACK_BISHOP = -3
    BLACK_ROOK = -4
    BLACK_QUEEN = -5
    BLACK_KING = -6


FEN_PIECE_LETTERS = {
    ChessPiece.WHITE_PAWN: "P",
    ChessPiece.WHITE_KNIGHT: "N",
    ChessPiece.WHITE_BISHOP: "B",
    ChessPiece.WHITE_ROOK: "R",
    ChessPiece.WHITE_QUEEN: "Q",
    ChessPiece.WHITE_KING: "K",
    ChessPiece.BLACK_PAWN: "p",
    ChessPiece.BLACK_KNIGHT: "n",
    ChessPiece.BLACK_BISHOP: "b",
    ChessPiece.BLACK_ROOK: "r",
    ChessPiece.BLACK_QUEEN: "q",
    ChessPiece.BLACK_KING: "k",
}
PIECE_FROM_FEN_LETTER = {letter: piece for piece, letter in FEN_PIECE_LETTERS.items()}

_UNICODE_GLYPHS = {
    ChessPiece.EMPTY: " ",
    ChessPiece.WHITE_KING: "♔",
    ChessPiece.WHITE_QUEEN: "♕",
    ChessPiece.WHITE_ROOK: "♖",
    ChessPiece.WHITE_BISHOP: "♗",
    ChessPiece.WHITE_KNIGHT: "♘",
    ChessPiece.WHITE_PAWN: "♙",
    ChessPiece.BLACK_KING: "♚",
    ChessPiece.BLACK_QUEEN: "♛",
    ChessPiece.BLACK_ROOK: "♜",
    ChessPiece.BLACK_BISHOP: "♝",
    ChessPiece.BLACK_KNIGHT: "♞",
    ChessPiece.BLACK_PAWN: "♟",
}


# Move ouside class attribute for optimization (less lookups)
# Important, because of for eample is_square_attacked that uses the value heavily
BOARD_SIZE = 8
SQUARE_COUNT = BOARD_SIZE * BOARD_SIZE


class ChessBoard(Board):
    def __init__(self, squares: list[ChessPiece]):
        self.squares = squares

    def get_piece(self, index: int) -> ChessPiece:
        return self.squares[index]

    def set_piece(self, index: int, piece: ChessPiece) -> None:
        self.squares[index] = piece

    def __str__(self) -> str:
        top = " ┌───" + (BOARD_SIZE - 1) * "┬───" + "┐\n"
        mid = " ├───" + (BOARD_SIZE - 1) * "┼───" + "┤\n"
        bot = " └───" + (BOARD_SIZE - 1) * "┴───" + "┘\n"

        string = top
        for row in range(BOARD_SIZE):
            line = " │"
            for col in range(BOARD_SIZE):
                piece = self.squares[square_index(row, col)]
                line += f" {_UNICODE_GLYPHS[piece]} │"
            string += line + "\n"
            if row != BOARD_SIZE - 1:
                string += mid
        string += bot
        return string


def square_index(row: int, col: int) -> int:
    return row * BOARD_SIZE + col


def square_row_col(index: int) -> tuple[int, int]:
    return divmod(index, BOARD_SIZE)


def square_color(index: int) -> int:
    row, col = square_row_col(index)
    return (row + col) % 2


def _algebraic_from_index(index: int) -> str:
    row, col = square_row_col(index)
    return f"{chr(ord('a') + col)}{BOARD_SIZE - row}"


_ALGEBRAIC_SQUARES = [_algebraic_from_index(index) for index in range(SQUARE_COUNT)]
_INDEX_BY_ALGEBRAIC = {square: index for index, square in enumerate(_ALGEBRAIC_SQUARES)}


def algebraic_to_index(square: str) -> int:
    return _INDEX_BY_ALGEBRAIC[square]


def index_to_algebraic(index: int) -> str:
    return _ALGEBRAIC_SQUARES[index]
