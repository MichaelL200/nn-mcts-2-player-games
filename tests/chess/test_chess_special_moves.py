from src.games.chess.board import ChessBoard, ChessPiece, algebraic_to_index
from src.games.chess.state import ChessState, ChessPlayer
from src.games.chess.movegen import generate_legal_moves, apply_move, advance


def _squares(pieces: dict[str, ChessPiece]) -> list[ChessPiece]:
    squares = [ChessPiece.EMPTY] * 64
    for square, piece in pieces.items():
        squares[algebraic_to_index(square)] = piece
    return squares


def _state(
    pieces: dict[str, ChessPiece],
    active_player: ChessPlayer = ChessPlayer.WHITE,
    castle_white_kingside: bool = False,
    castle_white_queenside: bool = False,
    castle_black_kingside: bool = False,
    castle_black_queenside: bool = False,
    en_passant: str | None = None,
) -> ChessState:
    return ChessState(
        ChessBoard(_squares(pieces)),
        active_player,
        castle_white_kingside,
        castle_white_queenside,
        castle_black_kingside,
        castle_black_queenside,
        algebraic_to_index(en_passant) if en_passant is not None else None,
        0,
        1,
    )


def test_white_kingside_castling_generated_when_legal():
    state = _state({"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK}, castle_white_kingside=True)
    assert "e1g1" in generate_legal_moves(state)


def test_white_queenside_castling_generated_when_legal():
    state = _state({"e1": ChessPiece.WHITE_KING, "a1": ChessPiece.WHITE_ROOK}, castle_white_queenside=True)
    assert "e1c1" in generate_legal_moves(state)


def test_black_kingside_castling_generated_when_legal():
    state = _state(
        {"e8": ChessPiece.BLACK_KING, "h8": ChessPiece.BLACK_ROOK},
        active_player=ChessPlayer.BLACK,
        castle_black_kingside=True,
    )
    assert "e8g8" in generate_legal_moves(state)


def test_castling_not_generated_without_the_right():
    state = _state({"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK})
    assert "e1g1" not in generate_legal_moves(state)


def test_castling_blocked_by_piece_between_king_and_rook():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK, "f1": ChessPiece.WHITE_BISHOP},
        castle_white_kingside=True,
    )
    assert "e1g1" not in generate_legal_moves(state)


def test_castling_not_allowed_while_in_check():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK, "e8": ChessPiece.BLACK_ROOK},
        castle_white_kingside=True,
    )
    assert "e1g1" not in generate_legal_moves(state)


def test_castling_not_allowed_through_attacked_square():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK, "f8": ChessPiece.BLACK_ROOK},
        castle_white_kingside=True,
    )
    assert "e1g1" not in generate_legal_moves(state)


def test_castling_not_allowed_into_attacked_square():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK, "g8": ChessPiece.BLACK_ROOK},
        castle_white_kingside=True,
    )
    assert "e1g1" not in generate_legal_moves(state)


def test_castling_moves_the_pieces():
    state = _state({"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK}, castle_white_kingside=True)
    board_after = apply_move(state.board, "e1g1")
    assert board_after.get_piece(algebraic_to_index("g1")) == ChessPiece.WHITE_KING
    assert board_after.get_piece(algebraic_to_index("f1")) == ChessPiece.WHITE_ROOK
    assert board_after.get_piece(algebraic_to_index("h1")) == ChessPiece.EMPTY
    assert board_after.get_piece(algebraic_to_index("e1")) == ChessPiece.EMPTY


def test_castling_rights_lost_after_king_moves():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "a1": ChessPiece.WHITE_ROOK, "h1": ChessPiece.WHITE_ROOK},
        castle_white_kingside=True,
        castle_white_queenside=True,
    )
    next_state = advance(state, "e1e2")
    assert next_state.castle_white_kingside is False
    assert next_state.castle_white_queenside is False


def test_castling_right_lost_after_rook_moves():
    state = _state({"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK}, castle_white_kingside=True)
    next_state = advance(state, "h1h2")
    assert next_state.castle_white_kingside is False


def test_castling_right_lost_after_rook_captured():
    state = _state(
        {"e1": ChessPiece.WHITE_KING, "h1": ChessPiece.WHITE_ROOK, "f2": ChessPiece.BLACK_KNIGHT},
        active_player=ChessPlayer.BLACK,
        castle_white_kingside=True,
    )
    next_state = advance(state, "f2h1")
    assert next_state.castle_white_kingside is False


def test_en_passant_capture_generated_when_available():
    state = _state(
        {"a1": ChessPiece.WHITE_KING, "e5": ChessPiece.WHITE_PAWN, "d5": ChessPiece.BLACK_PAWN}, en_passant="d6"
    )
    assert "e5d6" in generate_legal_moves(state)


def test_en_passant_not_generated_without_target():
    state = _state({"a1": ChessPiece.WHITE_KING, "e5": ChessPiece.WHITE_PAWN, "d5": ChessPiece.BLACK_PAWN})
    assert "e5d6" not in generate_legal_moves(state)


def test_en_passant_capture_removes_the_correct_pawn():
    state = _state({"e5": ChessPiece.WHITE_PAWN, "d5": ChessPiece.BLACK_PAWN}, en_passant="d6")
    board_after = apply_move(state.board, "e5d6")
    assert board_after.get_piece(algebraic_to_index("d6")) == ChessPiece.WHITE_PAWN
    assert board_after.get_piece(algebraic_to_index("d5")) == ChessPiece.EMPTY
    assert board_after.get_piece(algebraic_to_index("e5")) == ChessPiece.EMPTY


def test_en_passant_that_would_expose_own_king_is_rejected():
    state = _state(
        {
            "a5": ChessPiece.WHITE_KING,
            "e5": ChessPiece.WHITE_PAWN,
            "f5": ChessPiece.BLACK_PAWN,
            "h5": ChessPiece.BLACK_ROOK,
        },
        en_passant="f6",
    )
    moves = generate_legal_moves(state)
    assert "e5f6" not in moves
    assert "e5e6" in moves


def test_en_passant_target_set_after_double_push():
    state = _state({"e2": ChessPiece.WHITE_PAWN})
    next_state = advance(state, "e2e4")
    assert next_state.en_passant == algebraic_to_index("e3")


def test_en_passant_target_cleared_after_non_double_push_move():
    state = _state({"e2": ChessPiece.WHITE_PAWN}, en_passant="d6")
    next_state = advance(state, "e2e3")
    assert next_state.en_passant is None
