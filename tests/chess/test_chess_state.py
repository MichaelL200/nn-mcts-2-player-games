import pytest

from src.games.chess import ChessState, ChessPlayer
from src.games.chess.board import algebraic_to_index

FENS = [
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
    "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
    "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
    "4k3/8/8/8/8/8/8/4K3 w - - 0 1",
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1",
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
    "rnbqkbnr/1ppppppp/8/8/p7/8/PPPPPPPP/RNBQKBNR w KQkq a6 0 3",
    "rnbqkbnr/ppppppp1/8/8/7p/8/PPPPPPPP/RNBQKBNR w KQkq h6 0 3",
    "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w K - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w Q - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w k - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w q - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w Kk - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w Qq - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w KQk - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w KQq - 0 1",
    "r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1",
    "8/8/8/8/8/8/8/8 w - - 0 1",
    "k7/8/8/8/8/8/8/7K b - - 99 200",
]


@pytest.mark.parametrize("fen", FENS)
def test_fen_round_trip(fen):
    assert ChessState.from_fen(fen).to_fen() == fen


def test_from_fen_reads_active_player():
    assert ChessState.from_fen(FENS[0]).active_player == ChessPlayer.WHITE
    assert ChessState.from_fen(FENS[6]).active_player == ChessPlayer.BLACK


def test_from_fen_reads_castling_rights():
    state = ChessState.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w Kq - 0 1")

    assert state.castle_white_kingside is True
    assert state.castle_white_queenside is False
    assert state.castle_black_kingside is False
    assert state.castle_black_queenside is True


def test_from_fen_reads_en_passant_square():
    state = ChessState.from_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2")
    assert state.en_passant == algebraic_to_index("e6")


def test_from_fen_reads_no_en_passant():
    state = ChessState.from_fen(FENS[0])
    assert state.en_passant is None


def test_from_fen_reads_clocks():
    state = ChessState.from_fen("k7/8/8/8/8/8/8/7K b - - 99 200")
    assert state.halfmove_clock == 99
    assert state.fullmove_number == 200


def test_zobrist_equal_for_independently_built_identical_positions():
    a = ChessState.from_fen(FENS[0])
    b = ChessState.from_fen(FENS[0])
    assert a.zobrist_hash() == b.zobrist_hash()


def test_zobrist_differs_by_side_to_move():
    a = ChessState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    b = ChessState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")
    assert a.zobrist_hash() != b.zobrist_hash()


def test_zobrist_differs_by_castling_rights():
    a = ChessState.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    b = ChessState.from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQk - 0 1")
    assert a.zobrist_hash() != b.zobrist_hash()


def test_zobrist_differs_by_en_passant_file():
    a = ChessState.from_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2")
    b = ChessState.from_fen("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2")
    assert a.zobrist_hash() != b.zobrist_hash()
