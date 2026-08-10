from src.games.chess.board import ChessBoard, ChessPiece, algebraic_to_index
from src.games.chess.state import ChessState, ChessPlayer
from src.games.chess.movegen import generate_pseudo_legal_moves, is_square_attacked


def _squares(pieces: dict[str, ChessPiece]) -> list[ChessPiece]:
    squares = [ChessPiece.EMPTY] * 64
    for square, piece in pieces.items():
        squares[algebraic_to_index(square)] = piece
    return squares


def _state(pieces: dict[str, ChessPiece], active_player: ChessPlayer = ChessPlayer.WHITE) -> ChessState:
    return ChessState(ChessBoard(_squares(pieces)), active_player, False, False, False, False, None, 0, 1)


def _board(pieces: dict[str, ChessPiece]) -> ChessBoard:
    return ChessBoard(_squares(pieces))


def test_knight_moves_from_center():
    state = _state({"e4": ChessPiece.WHITE_KNIGHT})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e4c3", "e4c5", "e4d2", "e4d6", "e4f2", "e4f6", "e4g3", "e4g5"}


def test_knight_moves_from_corner():
    state = _state({"a1": ChessPiece.WHITE_KNIGHT})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"a1b3", "a1c2"}


def test_knight_cannot_capture_own_piece():
    state = _state({"e4": ChessPiece.WHITE_KNIGHT, "c3": ChessPiece.WHITE_PAWN})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("e4")}
    assert "e4c3" not in moves
    assert len(moves) == 7


def test_knight_can_capture_enemy_piece():
    state = _state({"e4": ChessPiece.WHITE_KNIGHT, "c3": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert "e4c3" in moves
    assert len(moves) == 8


def test_king_moves_from_center():
    state = _state({"e4": ChessPiece.WHITE_KING})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e4d3", "e4d4", "e4d5", "e4e3", "e4e5", "e4f3", "e4f4", "e4f5"}


def test_king_moves_from_corner():
    state = _state({"a1": ChessPiece.WHITE_KING})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"a1a2", "a1b1", "a1b2"}


def test_king_cannot_capture_own_piece():
    state = _state({"e4": ChessPiece.WHITE_KING, "e5": ChessPiece.WHITE_PAWN})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("e4")}
    assert "e4e5" not in moves
    assert len(moves) == 7


def test_king_can_capture_enemy_piece():
    state = _state({"e4": ChessPiece.WHITE_KING, "e5": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert "e4e5" in moves
    assert len(moves) == 8


def test_rook_moves_from_center():
    state = _state({"e4": ChessPiece.WHITE_ROOK})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "e4a4", "e4b4", "e4c4", "e4d4", "e4f4", "e4g4", "e4h4",
        "e4e1", "e4e2", "e4e3", "e4e5", "e4e6", "e4e7", "e4e8",
    }


def test_rook_moves_from_corner():
    state = _state({"a1": ChessPiece.WHITE_ROOK})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "a1b1", "a1c1", "a1d1", "a1e1", "a1f1", "a1g1", "a1h1",
        "a1a2", "a1a3", "a1a4", "a1a5", "a1a6", "a1a7", "a1a8",
    }


def test_rook_cannot_capture_own_piece():
    state = _state({"a1": ChessPiece.WHITE_ROOK, "a5": ChessPiece.WHITE_PAWN})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("a1")}
    assert {"a1a2", "a1a3", "a1a4"} <= moves
    assert not {"a1a5", "a1a6", "a1a7", "a1a8"} & moves
    assert len(moves) == 10


def test_rook_can_capture_enemy_piece():
    state = _state({"a1": ChessPiece.WHITE_ROOK, "a5": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert {"a1a2", "a1a3", "a1a4", "a1a5"} <= moves
    assert not {"a1a6", "a1a7", "a1a8"} & moves
    assert len(moves) == 11


def test_bishop_moves_from_center():
    state = _state({"e4": ChessPiece.WHITE_BISHOP})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "e4a8", "e4b7", "e4c6", "e4d5", "e4f5", "e4g6", "e4h7",
        "e4b1", "e4c2", "e4d3", "e4f3", "e4g2", "e4h1",
    }


def test_bishop_moves_from_corner():
    state = _state({"a1": ChessPiece.WHITE_BISHOP})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"a1b2", "a1c3", "a1d4", "a1e5", "a1f6", "a1g7", "a1h8"}


def test_bishop_cannot_capture_own_piece():
    state = _state({"a1": ChessPiece.WHITE_BISHOP, "e5": ChessPiece.WHITE_PAWN})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("a1")}
    assert {"a1b2", "a1c3", "a1d4"} <= moves
    assert not {"a1e5", "a1f6", "a1g7", "a1h8"} & moves
    assert len(moves) == 3


def test_bishop_can_capture_enemy_piece():
    state = _state({"a1": ChessPiece.WHITE_BISHOP, "e5": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert {"a1b2", "a1c3", "a1d4", "a1e5"} <= moves
    assert not {"a1f6", "a1g7", "a1h8"} & moves
    assert len(moves) == 4


def test_queen_moves_from_center():
    state = _state({"e4": ChessPiece.WHITE_QUEEN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "e4a4", "e4b4", "e4c4", "e4d4", "e4f4", "e4g4", "e4h4",
        "e4e1", "e4e2", "e4e3", "e4e5", "e4e6", "e4e7", "e4e8",
        "e4a8", "e4b7", "e4c6", "e4d5", "e4f5", "e4g6", "e4h7",
        "e4b1", "e4c2", "e4d3", "e4f3", "e4g2", "e4h1",
    }


def test_queen_moves_from_corner():
    state = _state({"a1": ChessPiece.WHITE_QUEEN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "a1a2", "a1a3", "a1a4", "a1a5", "a1a6", "a1a7", "a1a8",
        "a1b1", "a1c1", "a1d1", "a1e1", "a1f1", "a1g1", "a1h1",
        "a1b2", "a1c3", "a1d4", "a1e5", "a1f6", "a1g7", "a1h8",
    }


def test_queen_cannot_capture_own_piece():
    state = _state({"a1": ChessPiece.WHITE_QUEEN, "e5": ChessPiece.WHITE_PAWN})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("a1")}
    assert {"a1b2", "a1c3", "a1d4"} <= moves
    assert not {"a1e5", "a1f6", "a1g7", "a1h8"} & moves
    assert len(moves) == 17


def test_queen_can_capture_enemy_piece():
    state = _state({"a1": ChessPiece.WHITE_QUEEN, "e5": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert {"a1b2", "a1c3", "a1d4", "a1e5"} <= moves
    assert not {"a1f6", "a1g7", "a1h8"} & moves
    assert len(moves) == 18


def test_pawn_single_push_when_not_on_start_rank():
    state = _state({"e4": ChessPiece.WHITE_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e4e5"}


def test_pawn_double_push_from_start_rank():
    state = _state({"e2": ChessPiece.WHITE_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e2e3", "e2e4"}


def test_pawn_blocked_directly_ahead_prevents_push_and_double_push():
    state = _state({"e2": ChessPiece.WHITE_PAWN, "e3": ChessPiece.BLACK_KNIGHT})
    moves = {m for m in generate_pseudo_legal_moves(state) if m.startswith("e2")}
    assert moves == set()


def test_pawn_diagonal_capture():
    state = _state({"e4": ChessPiece.WHITE_PAWN, "d5": ChessPiece.BLACK_PAWN, "f5": ChessPiece.BLACK_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e4e5", "e4d5", "e4f5"}


def test_pawn_cannot_move_diagonally_into_empty_square():
    state = _state({"e4": ChessPiece.WHITE_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert "e4d5" not in moves
    assert "e4f5" not in moves


def test_pawn_promotion_on_push():
    state = _state({"e7": ChessPiece.WHITE_PAWN})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e7e8q", "e7e8r", "e7e8b", "e7e8n"}


def test_pawn_promotion_on_capture():
    state = _state({"e7": ChessPiece.WHITE_PAWN, "d8": ChessPiece.BLACK_ROOK})
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {
        "e7e8q", "e7e8r", "e7e8b", "e7e8n",
        "e7d8q", "e7d8r", "e7d8b", "e7d8n",
    }


def test_black_pawn_moves_in_opposite_direction():
    state = _state({"e7": ChessPiece.BLACK_PAWN}, active_player=ChessPlayer.BLACK)
    moves = set(generate_pseudo_legal_moves(state))
    assert moves == {"e7e6", "e7e5"}


def test_pawn_attacks_diagonals_not_straight_ahead():
    board = _board({"e4": ChessPiece.WHITE_PAWN})
    assert is_square_attacked(board, algebraic_to_index("d5"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("f5"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("e5"), ChessPlayer.WHITE) is False


def test_knight_attacks_its_l_shaped_squares():
    board = _board({"e4": ChessPiece.WHITE_KNIGHT})
    assert is_square_attacked(board, algebraic_to_index("d6"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("e5"), ChessPlayer.WHITE) is False


def test_king_attacks_adjacent_squares_only():
    board = _board({"e4": ChessPiece.WHITE_KING})
    assert is_square_attacked(board, algebraic_to_index("d5"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("c3"), ChessPlayer.WHITE) is False


def test_slider_attacks_include_the_blocking_square_itself():
    board = _board({"a1": ChessPiece.WHITE_ROOK, "a3": ChessPiece.WHITE_PAWN})
    assert is_square_attacked(board, algebraic_to_index("a2"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("a3"), ChessPlayer.WHITE) is True
    assert is_square_attacked(board, algebraic_to_index("a4"), ChessPlayer.WHITE) is False


def test_is_square_attacked_respects_color():
    board = _board({"e4": ChessPiece.WHITE_PAWN})
    assert is_square_attacked(board, algebraic_to_index("d5"), ChessPlayer.BLACK) is False
