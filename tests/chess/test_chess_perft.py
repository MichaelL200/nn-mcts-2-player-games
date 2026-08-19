import pytest

from src.games.chess.state import ChessState
from src.games.chess.movegen import generate_legal_moves, advance

# positions and expected counts: https://www.chessprogramming.org/Perft_Results
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
KIWIPETE_FEN = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"
POSITION_3_FEN = "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"
POSITION_4_FEN = "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"
POSITION_5_FEN = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"


def _perft(state: ChessState, depth: int) -> int:
    if depth == 0:
        return 1
    return sum(_perft(advance(state, move), depth - 1) for move in generate_legal_moves(state))


def test_perft_from_start_position():
    state = ChessState.from_fen(START_FEN)
    assert _perft(state, 1) == 20
    assert _perft(state, 2) == 400
    assert _perft(state, 3) == 8902
    assert _perft(state, 4) == 197281


@pytest.mark.parametrize(
    "fen, depth, expected",
    [
        (KIWIPETE_FEN, 1, 48),
        (KIWIPETE_FEN, 2, 2039),
        (KIWIPETE_FEN, 3, 97862),
        (POSITION_3_FEN, 1, 14),
        (POSITION_3_FEN, 2, 191),
        (POSITION_3_FEN, 3, 2812),
        (POSITION_4_FEN, 1, 6),
        (POSITION_4_FEN, 2, 264),
        (POSITION_4_FEN, 3, 9467),
        (POSITION_5_FEN, 1, 44),
        (POSITION_5_FEN, 2, 1486),
        (POSITION_5_FEN, 3, 62379),
    ],
)
def test_perft_standard_positions(fen, depth, expected):
    assert _perft(ChessState.from_fen(fen), depth) == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "fen, depth, expected",
    [
        (START_FEN, 5, 4865609),
        (KIWIPETE_FEN, 4, 4085603),
        (POSITION_3_FEN, 5, 674624),
        (POSITION_4_FEN, 4, 422333),
        (POSITION_5_FEN, 4, 2103487),
    ],
)
def test_perft_deep_standard_positions(fen, depth, expected):
    assert _perft(ChessState.from_fen(fen), depth) == expected
