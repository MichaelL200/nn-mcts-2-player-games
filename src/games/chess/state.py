import random
from enum import Enum

from ...core.interfaces import GameState
from .board import (
    ChessBoard,
    ChessPiece,
    FEN_PIECE_LETTERS,
    PIECE_FROM_FEN_LETTER,
    algebraic_to_index,
    index_to_algebraic,
    square_index,
    square_row_col,
)


class ChessPlayer(Enum):
    WHITE = 1
    BLACK = -1


_ZOBRIST_RNG = random.Random(0xC0FFEE)
_PIECE_SQUARE_HASHES = {
    (piece, index): _ZOBRIST_RNG.getrandbits(64)
    for piece in ChessPiece
    if piece != ChessPiece.EMPTY
    for index in range(64)
}
_SIDE_TO_MOVE_HASH = _ZOBRIST_RNG.getrandbits(64)
# one number per still-available castling right: White/Black king/queenside, as in FEN's "KQkq" field
_CASTLING_HASHES = {right: _ZOBRIST_RNG.getrandbits(64) for right in "KQkq"}
# one number per file (column a-h); the en passant square's rank is implied by whose turn it is
_EN_PASSANT_FILE_HASHES = [_ZOBRIST_RNG.getrandbits(64) for _ in range(8)]


class ChessState(GameState):
    def __init__(
        self,
        board: ChessBoard,
        active_player: ChessPlayer,
        castle_white_kingside: bool,
        castle_white_queenside: bool,
        castle_black_kingside: bool,
        castle_black_queenside: bool,
        en_passant: int | None,  # indicates if en_passant is possible and where
        halfmove_clock: int,  # counter for fifty-move rule
        fullmove_number: int,  # the current round (starts form 1)
    ) -> None:
        self.board = board
        self.active_player = active_player
        self.castle_white_kingside = castle_white_kingside
        self.castle_white_queenside = castle_white_queenside
        self.castle_black_kingside = castle_black_kingside
        self.castle_black_queenside = castle_black_queenside
        self.en_passant = en_passant
        self.halfmove_clock = halfmove_clock
        self.fullmove_number = fullmove_number

    @classmethod
    def from_fen(cls, fen: str) -> "ChessState":
        placement, active_color, castling, en_passant, halfmove_clock, fullmove_number = fen.split(" ")

        squares = [ChessPiece.EMPTY] * 64
        for row, rank in enumerate(placement.split("/")):
            col = 0
            for char in rank:
                if char.isdigit():
                    col += int(char)
                else:
                    squares[square_index(row, col)] = PIECE_FROM_FEN_LETTER[char]
                    col += 1

        return cls(
            board=ChessBoard(squares),
            active_player=ChessPlayer.WHITE if active_color == "w" else ChessPlayer.BLACK,
            castle_white_kingside="K" in castling,
            castle_white_queenside="Q" in castling,
            castle_black_kingside="k" in castling,
            castle_black_queenside="q" in castling,
            en_passant=None if en_passant == "-" else algebraic_to_index(en_passant),
            halfmove_clock=int(halfmove_clock),
            fullmove_number=int(fullmove_number),
        )

    def to_fen(self) -> str:
        rows = []
        for row in range(8):
            rank = ""
            empty_run = 0
            for col in range(8):
                piece = self.board.get_piece(square_index(row, col))
                if piece == ChessPiece.EMPTY:
                    empty_run += 1
                    continue
                if empty_run:
                    rank += str(empty_run)
                    empty_run = 0
                rank += FEN_PIECE_LETTERS[piece]
            if empty_run:
                rank += str(empty_run)
            rows.append(rank)
        placement = "/".join(rows)

        active_color = "w" if self.active_player == ChessPlayer.WHITE else "b"

        castling = (
            ("K" if self.castle_white_kingside else "")
            + ("Q" if self.castle_white_queenside else "")
            + ("k" if self.castle_black_kingside else "")
            + ("q" if self.castle_black_queenside else "")
        ) or "-"

        en_passant = "-" if self.en_passant is None else index_to_algebraic(self.en_passant)

        return f"{placement} {active_color} {castling} {en_passant} {self.halfmove_clock} {self.fullmove_number}"

    def zobrist_hash(self) -> int:
        digest = 0
        for index, piece in enumerate(self.board.squares):
            if piece != ChessPiece.EMPTY:
                digest ^= _PIECE_SQUARE_HASHES[(piece, index)]

        if self.active_player == ChessPlayer.BLACK:
            digest ^= _SIDE_TO_MOVE_HASH
        if self.castle_white_kingside:
            digest ^= _CASTLING_HASHES["K"]
        if self.castle_white_queenside:
            digest ^= _CASTLING_HASHES["Q"]
        if self.castle_black_kingside:
            digest ^= _CASTLING_HASHES["k"]
        if self.castle_black_queenside:
            digest ^= _CASTLING_HASHES["q"]
        if self.en_passant is not None:
            _, col = square_row_col(self.en_passant)
            digest ^= _EN_PASSANT_FILE_HASHES[col]

        return digest
