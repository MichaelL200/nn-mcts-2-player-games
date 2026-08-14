from src.games.chess.state import ChessState, ChessPlayer
from src.games.chess.movegen import generate_legal_moves, apply_move


def _advance(state: ChessState, move: str) -> ChessState:
    board = apply_move(state.board, move)
    next_player = ChessPlayer.BLACK if state.active_player == ChessPlayer.WHITE else ChessPlayer.WHITE
    return ChessState(board, next_player, False, False, False, False, None, 0, 1)


def _perft(state: ChessState, depth: int) -> int:
    if depth == 0:
        return 1
    return sum(_perft(_advance(state, move), depth - 1) for move in generate_legal_moves(state))


def test_perft_from_start_position():
    state = ChessState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    assert _perft(state, 1) == 20
    assert _perft(state, 2) == 400
    assert _perft(state, 3) == 8902
    assert _perft(state, 4) == 197281
