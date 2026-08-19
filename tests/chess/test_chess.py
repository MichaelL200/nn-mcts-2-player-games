import numpy as np
import pytest

from src.games.chess.board import ChessBoard, ChessPiece, algebraic_to_index
from src.games.chess.state import ChessState, ChessPlayer
from src.games.chess.chess import Chess


def _squares(pieces: dict[str, ChessPiece]) -> list[ChessPiece]:
    squares = [ChessPiece.EMPTY] * 64
    for square, piece in pieces.items():
        squares[algebraic_to_index(square)] = piece
    return squares


def _state(
    pieces: dict[str, ChessPiece],
    active_player: ChessPlayer = ChessPlayer.WHITE,
    halfmove_clock: int = 0,
) -> ChessState:
    return ChessState(
        ChessBoard(_squares(pieces)), active_player, False, False, False, False, None, halfmove_clock, 1, []
    )


def test_checkmate_reward_is_plus_one_for_mater_and_minus_one_for_mated():
    state = _state(
        {
            "a1": ChessPiece.WHITE_KING,
            "a8": ChessPiece.WHITE_ROOK,
            "g8": ChessPiece.BLACK_KING,
            "f7": ChessPiece.BLACK_PAWN,
            "g7": ChessPiece.BLACK_PAWN,
            "h7": ChessPiece.BLACK_PAWN,
        },
        active_player=ChessPlayer.BLACK,
    )
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 1
    assert game.reward(state, ChessPlayer.BLACK) == -1


def test_fifty_move_rule_is_a_draw():
    state = ChessState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 100 50")
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0
    assert game.reward(state, ChessPlayer.BLACK) == 0


def test_halfmove_clock_below_hundred_is_not_a_draw():
    state = ChessState.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 99 50")
    assert Chess().is_terminal(state) is False


def test_threefold_repetition_is_a_draw():
    state = _state({"a1": ChessPiece.WHITE_KING, "h8": ChessPiece.BLACK_KING, "a8": ChessPiece.BLACK_QUEEN})
    repeated_hash = state.zobrist_hash()
    state.position_history = [repeated_hash, repeated_hash, repeated_hash]
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_position_seen_only_twice_is_not_a_draw():
    state = _state({"a1": ChessPiece.WHITE_KING, "h8": ChessPiece.BLACK_KING, "a8": ChessPiece.BLACK_QUEEN})
    repeated_hash = state.zobrist_hash()
    state.position_history = [repeated_hash, repeated_hash]
    assert Chess().is_terminal(state) is False


def test_repeated_king_shuffle_ends_in_threefold_repetition_draw():
    game = Chess()
    state = ChessState.from_fen("4k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    moves = ["e1e2", "e8e7", "e2e1", "e7e8"] * 3
    for move in moves:
        state = game.make_move(state, move)
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_king_vs_king_is_insufficient_material():
    state = _state({"a1": ChessPiece.WHITE_KING, "h8": ChessPiece.BLACK_KING})
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_king_and_knight_vs_king_is_insufficient_material():
    state = _state({"a1": ChessPiece.WHITE_KING, "h8": ChessPiece.BLACK_KING, "b1": ChessPiece.WHITE_KNIGHT})
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_king_and_bishop_vs_king_is_insufficient_material():
    state = _state({"a1": ChessPiece.WHITE_KING, "h8": ChessPiece.BLACK_KING, "b1": ChessPiece.WHITE_BISHOP})
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_king_and_bishop_vs_king_and_same_color_bishop_is_insufficient_material():
    state = _state(
        {
            "a1": ChessPiece.WHITE_KING,
            "h8": ChessPiece.BLACK_KING,
            "c1": ChessPiece.WHITE_BISHOP,
            "f4": ChessPiece.BLACK_BISHOP,
        }
    )
    game = Chess()
    assert game.is_terminal(state) is True
    assert game.reward(state, ChessPlayer.WHITE) == 0


def test_king_and_bishop_vs_king_and_opposite_color_bishop_is_not_insufficient_material():
    state = _state(
        {
            "a1": ChessPiece.WHITE_KING,
            "h8": ChessPiece.BLACK_KING,
            "c1": ChessPiece.WHITE_BISHOP,
            "d1": ChessPiece.BLACK_BISHOP,
        }
    )
    assert Chess().is_terminal(state) is False


@pytest.mark.slow
def test_move_to_index_is_injective_across_many_random_positions():
    np.random.seed(42)
    game = Chess()
    sampled_states = []

    while len(sampled_states) < 1000:
        state = game.get_starting_state()
        for _ in range(200):
            if game.is_terminal(state) or len(sampled_states) >= 1000:
                break
            sampled_states.append(state)
            state = game.make_random_move(state)

    for state in sampled_states:
        moves = game.get_moves(state)
        indices = [game.encoder.move_to_index(move) for move in moves]
        assert len(indices) == len(set(indices))


def test_encode_shape_is_correct():
    game = Chess()
    tensor = game.encoder.encode(game.get_starting_state())
    assert tuple(tensor.shape) == (1, 19, 8, 8)


def test_encode_start_position_matches_expected_planes():
    game = Chess()
    tensor = game.encoder.encode(game.get_starting_state())

    # The 64 are for boolean information encoded in full 8x8 plane since we cannot change the shape just for them
    assert tensor[0, 0, 6, 4].item() == 1.0  # white pawn on e2
    assert tensor[0, 5, 7, 4].item() == 1.0  # white king on e1
    assert tensor[0, 6, 1, 4].item() == 1.0  # black pawn on e7
    assert tensor[0, 11, 0, 4].item() == 1.0  # black king on e8
    assert tensor[0, 12, :, :].sum().item() == 64  # white to move
    assert tensor[0, 13, :, :].sum().item() == 64  # white kingside right
    assert tensor[0, 14, :, :].sum().item() == 64  # white queenside right
    assert tensor[0, 15, :, :].sum().item() == 64  # black kingside right
    assert tensor[0, 16, :, :].sum().item() == 64  # black queenside right
    assert tensor[0, 17, :, :].sum().item() == 0  # no en passant target yet
    assert tensor[0, 18, :, :].sum().item() == 0  # halfmove clock is zero
