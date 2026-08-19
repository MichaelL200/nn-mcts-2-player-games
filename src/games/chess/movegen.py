from ...core.interfaces import Move
from .board import ChessBoard, ChessPiece, square_index, square_row_col, index_to_algebraic, algebraic_to_index
from .state import ChessState, ChessPlayer, piece_color

_KNIGHT_OFFSETS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
_KING_OFFSETS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
_BISHOP_DIRECTIONS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
_ROOK_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
_QUEEN_DIRECTIONS = _BISHOP_DIRECTIONS + _ROOK_DIRECTIONS

_PROMOTION_PIECES = "qrbn"
_WHITE_PROMOTION_PIECE_BY_LETTER = {
    "q": ChessPiece.WHITE_QUEEN,
    "r": ChessPiece.WHITE_ROOK,
    "b": ChessPiece.WHITE_BISHOP,
    "n": ChessPiece.WHITE_KNIGHT,
}

_WHITE_KING_START = algebraic_to_index("e1")
_WHITE_KINGSIDE_ROOK_START = algebraic_to_index("h1")
_WHITE_QUEENSIDE_ROOK_START = algebraic_to_index("a1")
_WHITE_KINGSIDE_CASTLE_TARGET = algebraic_to_index("g1")
_WHITE_QUEENSIDE_CASTLE_TARGET = algebraic_to_index("c1")
_WHITE_KINGSIDE_CASTLE_EMPTY_SQUARES = (algebraic_to_index("f1"), algebraic_to_index("g1"))
_WHITE_QUEENSIDE_CASTLE_EMPTY_SQUARES = (algebraic_to_index("b1"), algebraic_to_index("c1"), algebraic_to_index("d1"))

_BLACK_KING_START = algebraic_to_index("e8")
_BLACK_KINGSIDE_ROOK_START = algebraic_to_index("h8")
_BLACK_QUEENSIDE_ROOK_START = algebraic_to_index("a8")
_BLACK_KINGSIDE_CASTLE_TARGET = algebraic_to_index("g8")
_BLACK_QUEENSIDE_CASTLE_TARGET = algebraic_to_index("c8")
_BLACK_KINGSIDE_CASTLE_EMPTY_SQUARES = (algebraic_to_index("f8"), algebraic_to_index("g8"))
_BLACK_QUEENSIDE_CASTLE_EMPTY_SQUARES = (algebraic_to_index("b8"), algebraic_to_index("c8"), algebraic_to_index("d8"))


def is_checkmate(state: ChessState) -> bool:
    return is_in_check(state) and not generate_legal_moves(state)


def is_stalemate(state: ChessState) -> bool:
    return not is_in_check(state) and not generate_legal_moves(state)


def is_in_check(state: ChessState) -> bool:
    return _king_in_check(state.board, state.active_player)


def is_draw_by_fifty_move_rule(state: ChessState) -> bool:
    return state.halfmove_clock >= 100


def is_draw_by_repetition(state: ChessState) -> bool:
    return state.position_history.count(state.zobrist_hash()) >= 3


def has_insufficient_material(board: ChessBoard) -> bool:
    non_king_pieces = [
        (index, piece)
        for index, piece in enumerate(board.squares)
        if piece not in (ChessPiece.EMPTY, ChessPiece.WHITE_KING, ChessPiece.BLACK_KING)
    ]

    if len(non_king_pieces) == 0:
        return True

    if len(non_king_pieces) == 1:
        _, piece = non_king_pieces[0]
        return piece in (
                ChessPiece.WHITE_KNIGHT,
                ChessPiece.BLACK_KNIGHT,
                ChessPiece.WHITE_BISHOP,
                ChessPiece.BLACK_BISHOP,
            )

    if len(non_king_pieces) == 2:
        (first_index, first_piece), (second_index, second_piece) = non_king_pieces
        both_bishops = (
            first_piece in (ChessPiece.WHITE_BISHOP, ChessPiece.BLACK_BISHOP)
            and second_piece in (ChessPiece.WHITE_BISHOP, ChessPiece.BLACK_BISHOP)
        )
        return both_bishops and _square_color(first_index) == _square_color(second_index)

    return False


def generate_legal_moves(state: ChessState) -> list[Move]:
    if state._legal_moves_cache is not None:
        return list(state._legal_moves_cache)
    color = state.active_player
    legal_moves = []
    for move in generate_pseudo_legal_moves(state):
        board_after = apply_move(state.board, move)
        if not _king_in_check(board_after, color):
            legal_moves.append(move)
    state._legal_moves_cache = legal_moves
    return list(legal_moves)


def advance(state: ChessState, move: Move) -> ChessState:
    from_square, to_square, _ = parse_move(move)
    touched = {from_square, to_square}

    next_state = ChessState(
        apply_move(state.board, move),
        enemy_color(state.active_player),
        _still_has_right(state.castle_white_kingside, touched, _WHITE_KING_START, _WHITE_KINGSIDE_ROOK_START),
        _still_has_right(state.castle_white_queenside, touched, _WHITE_KING_START, _WHITE_QUEENSIDE_ROOK_START),
        _still_has_right(state.castle_black_kingside, touched, _BLACK_KING_START, _BLACK_KINGSIDE_ROOK_START),
        _still_has_right(state.castle_black_queenside, touched, _BLACK_KING_START, _BLACK_QUEENSIDE_ROOK_START),
        _new_en_passant_target(state.board, from_square, to_square),
        _next_halfmove_clock(state.board, from_square, to_square, state.halfmove_clock),
        _next_fullmove_number(state.active_player, state.fullmove_number),
        [],
    )
    next_state.position_history = state.position_history + [next_state.zobrist_hash()]
    return next_state


def apply_move(board: ChessBoard, move: Move) -> ChessBoard:
    from_square, to_square, promotion = parse_move(move)
    squares = board.squares.copy()
    moving_piece = squares[from_square]

    squares[from_square] = ChessPiece.EMPTY
    squares[to_square] = _promoted_piece(promotion, piece_color(moving_piece)) if promotion else moving_piece

    # Castling
    if moving_piece in (ChessPiece.WHITE_KING, ChessPiece.BLACK_KING) and abs(to_square - from_square) == 2:
        _move_castling_rook(squares, from_square, to_square)
    # En passant
    elif (
        moving_piece in (ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN)
        and board.get_piece(to_square) == ChessPiece.EMPTY
        and to_square % 8 != from_square % 8
    ):
        captured_row, _ = square_row_col(from_square)
        _, captured_col = square_row_col(to_square)
        squares[square_index(captured_row, captured_col)] = ChessPiece.EMPTY

    return ChessBoard(squares)


def parse_move(move: Move) -> tuple[int, int, str | None]:
    from_square = algebraic_to_index(move[0:2])
    to_square = algebraic_to_index(move[2:4])
    promotion = move[4] if len(move) > 4 else None
    return from_square, to_square, promotion


def generate_pseudo_legal_moves(state: ChessState) -> list[Move]:
    board = state.board
    color = state.active_player
    moves = []
    for index, piece in enumerate(board.squares):
        if piece == ChessPiece.EMPTY or piece_color(piece) != color:
            continue
        match piece:
            case ChessPiece.WHITE_PAWN | ChessPiece.BLACK_PAWN:
                moves += _pawn_moves(state, index)
            case ChessPiece.WHITE_KNIGHT | ChessPiece.BLACK_KNIGHT:
                moves += _leaper_moves(board, color, index, _KNIGHT_OFFSETS)
            case ChessPiece.WHITE_BISHOP | ChessPiece.BLACK_BISHOP:
                moves += _slider_moves(board, color, index, _BISHOP_DIRECTIONS)
            case ChessPiece.WHITE_ROOK | ChessPiece.BLACK_ROOK:
                moves += _slider_moves(board, color, index, _ROOK_DIRECTIONS)
            case ChessPiece.WHITE_QUEEN | ChessPiece.BLACK_QUEEN:
                moves += _slider_moves(board, color, index, _QUEEN_DIRECTIONS)
            case ChessPiece.WHITE_KING | ChessPiece.BLACK_KING:
                moves += _leaper_moves(board, color, index, _KING_OFFSETS)
                moves += _castling_moves(state)
    return moves


def is_square_attacked(board: ChessBoard, square: int, by_color: ChessPlayer) -> bool:
    squares = board.squares
    row, col = square_row_col(square)
    sign = 1 if by_color == ChessPlayer.WHITE else -1
    knight = ChessPiece(ChessPiece.WHITE_KNIGHT * sign)
    king = ChessPiece(ChessPiece.WHITE_KING * sign)
    pawn = ChessPiece(ChessPiece.WHITE_PAWN * sign)
    bishop = ChessPiece(ChessPiece.WHITE_BISHOP * sign)
    rook = ChessPiece(ChessPiece.WHITE_ROOK * sign)
    queen = ChessPiece(ChessPiece.WHITE_QUEEN * sign)

    if _attacked_by_leaper(squares, row, col, _KNIGHT_OFFSETS, knight):
        return True

    if _attacked_by_leaper(squares, row, col, _KING_OFFSETS, king):
        return True

    if _attacked_by_pawn(squares, row, col, by_color, pawn):
        return True

    if _attacked_by_slider(squares, row, col, _BISHOP_DIRECTIONS, bishop, queen):
        return True

    if _attacked_by_slider(squares, row, col, _ROOK_DIRECTIONS, rook, queen):
        return True

    return False


def _attacked_by_leaper(
    squares: list[ChessPiece], row: int, col: int, offsets: list[tuple[int, int]], piece: ChessPiece
) -> bool:
    for d_row, d_col in offsets:
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < 8 and 0 <= new_col < 8 and squares[square_index(new_row, new_col)] == piece:
            return True
    return False


def _attacked_by_pawn(squares: list[ChessPiece], row: int, col: int, by_color: ChessPlayer, pawn: ChessPiece) -> bool:
    pawn_row = row + 1 if by_color == ChessPlayer.WHITE else row - 1
    if not 0 <= pawn_row < 8:
        return False
    for d_col in (-1, 1):
        new_col = col + d_col
        if 0 <= new_col < 8 and squares[square_index(pawn_row, new_col)] == pawn:
            return True
    return False


def _attacked_by_slider(
    squares: list[ChessPiece],
    row: int,
    col: int,
    directions: list[tuple[int, int]],
    piece_a: ChessPiece,
    piece_b: ChessPiece,
) -> bool:
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            occupant = squares[square_index(new_row, new_col)]
            if occupant != ChessPiece.EMPTY:
                if occupant == piece_a or occupant == piece_b:
                    return True
                break
            new_row += d_row
            new_col += d_col
    return False


def _king_in_check(board: ChessBoard, color: ChessPlayer) -> bool:
    king_square = _king_square(board, color)
    return is_square_attacked(board, king_square, enemy_color(color))


def _still_has_right(currently_held: bool, touched: set[int], king_start: int, rook_start: int) -> bool:
    return currently_held and king_start not in touched and rook_start not in touched


def _new_en_passant_target(board_before: ChessBoard, from_square: int, to_square: int) -> int | None:
    moving_piece = board_before.get_piece(from_square)
    # If double move of a pawn
    if moving_piece in (ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN) and abs(to_square - from_square) == 16:
        return (from_square + to_square) // 2
    return None


def _square_color(index: int) -> int:
    row, col = square_row_col(index)
    return (row + col) % 2


def _next_halfmove_clock(board_before: ChessBoard, from_square: int, to_square: int, current_clock: int) -> int:
    moving_piece = board_before.get_piece(from_square)
    is_pawn_move = moving_piece in (ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN)
    is_capture = board_before.get_piece(to_square) != ChessPiece.EMPTY
    if is_pawn_move or is_capture:
        return 0
    return current_clock + 1


def _next_fullmove_number(color: ChessPlayer, current_number: int) -> int:
    return current_number + 1 if color == ChessPlayer.BLACK else current_number


def _move_castling_rook(squares: list[ChessPiece], king_from: int, king_to: int) -> None:
    row, _ = square_row_col(king_from)
    if king_to > king_from:
        rook_from, rook_to = square_index(row, 7), square_index(row, 5)
    else:
        rook_from, rook_to = square_index(row, 0), square_index(row, 3)
    squares[rook_to] = squares[rook_from]
    squares[rook_from] = ChessPiece.EMPTY


def _promoted_piece(promotion: str, color: ChessPlayer) -> ChessPiece:
    white_piece = _WHITE_PROMOTION_PIECE_BY_LETTER[promotion]
    return white_piece if color == ChessPlayer.WHITE else ChessPiece(-white_piece)


def _king_square(board: ChessBoard, color: ChessPlayer) -> int:
    king = ChessPiece.WHITE_KING if color == ChessPlayer.WHITE else ChessPiece.BLACK_KING
    return board.squares.index(king)


def enemy_color(color: ChessPlayer) -> ChessPlayer:
    return ChessPlayer.BLACK if color == ChessPlayer.WHITE else ChessPlayer.WHITE


def _leaper_targets(index: int, offsets: list[tuple[int, int]]) -> list[int]:
    row, col = square_row_col(index)
    targets = []
    for d_row, d_col in offsets:
        new_row, new_col = row + d_row, col + d_col
        if 0 <= new_row < 8 and 0 <= new_col < 8:
            targets.append(square_index(new_row, new_col))
    return targets


def _slider_targets(board: ChessBoard, index: int, directions: list[tuple[int, int]]) -> list[int]:
    row, col = square_row_col(index)
    targets = []
    for d_row, d_col in directions:
        new_row, new_col = row + d_row, col + d_col
        while 0 <= new_row < 8 and 0 <= new_col < 8:
            target = square_index(new_row, new_col)
            targets.append(target)
            if board.get_piece(target) != ChessPiece.EMPTY:
                break
            new_row += d_row
            new_col += d_col
    return targets


def _leaper_moves(board: ChessBoard, color: ChessPlayer, index: int, offsets: list[tuple[int, int]]) -> list[Move]:
    moves = []
    for target in _leaper_targets(index, offsets):
        occupant = board.get_piece(target)
        if occupant == ChessPiece.EMPTY or piece_color(occupant) != color:
            moves.append(_move_string(index, target))
    return moves


def _slider_moves(board: ChessBoard, color: ChessPlayer, index: int, directions: list[tuple[int, int]]) -> list[Move]:
    moves = []
    for target in _slider_targets(board, index, directions):
        occupant = board.get_piece(target)
        if occupant == ChessPiece.EMPTY or piece_color(occupant) != color:
            moves.append(_move_string(index, target))
    return moves


def _pawn_moves(state: ChessState, index: int) -> list[Move]:
    board = state.board
    color = state.active_player
    row, col = square_row_col(index)
    direction = -1 if color == ChessPlayer.WHITE else 1
    target_row = row + direction

    if not 0 <= target_row < 8:
        return []

    is_promotion = target_row == (0 if color == ChessPlayer.WHITE else 7)
    start_row = 6 if color == ChessPlayer.WHITE else 1

    moves = []

    push_target = square_index(target_row, col)
    if board.get_piece(push_target) == ChessPiece.EMPTY:
        moves += _pawn_destinations(index, push_target, is_promotion)

        if row == start_row:
            double_push_target = square_index(row + 2 * direction, col)
            if board.get_piece(double_push_target) == ChessPiece.EMPTY:
                moves.append(_move_string(index, double_push_target))

    for d_col in (-1, 1):
        target_col = col + d_col
        if 0 <= target_col < 8:
            capture_target = square_index(target_row, target_col)
            occupant = board.get_piece(capture_target)
            if occupant != ChessPiece.EMPTY and piece_color(occupant) != color:
                moves += _pawn_destinations(index, capture_target, is_promotion)
            elif capture_target == state.en_passant:
                moves.append(_move_string(index, capture_target))

    return moves


def _castling_moves(state: ChessState) -> list[Move]:
    moves = []
    if state.active_player == ChessPlayer.WHITE:
        if state.castle_white_kingside:
            moves += _castling_move_if_legal(
                state, _WHITE_KING_START, _WHITE_KINGSIDE_CASTLE_TARGET, _WHITE_KINGSIDE_CASTLE_EMPTY_SQUARES
            )
        if state.castle_white_queenside:
            moves += _castling_move_if_legal(
                state, _WHITE_KING_START, _WHITE_QUEENSIDE_CASTLE_TARGET, _WHITE_QUEENSIDE_CASTLE_EMPTY_SQUARES
            )
    else:
        if state.castle_black_kingside:
            moves += _castling_move_if_legal(
                state, _BLACK_KING_START, _BLACK_KINGSIDE_CASTLE_TARGET, _BLACK_KINGSIDE_CASTLE_EMPTY_SQUARES
            )
        if state.castle_black_queenside:
            moves += _castling_move_if_legal(
                state, _BLACK_KING_START, _BLACK_QUEENSIDE_CASTLE_TARGET, _BLACK_QUEENSIDE_CASTLE_EMPTY_SQUARES
            )
    return moves


def _castling_move_if_legal(
    state: ChessState, king_from: int, king_to: int, empty_squares: tuple[int, ...]
) -> list[Move]:
    board = state.board
    enemy = enemy_color(state.active_player)

    if any(board.get_piece(square) != ChessPiece.EMPTY for square in empty_squares):
        return []

    transit_square = (king_from + king_to) // 2
    if any(is_square_attacked(board, square, enemy) for square in (king_from, transit_square, king_to)):
        return []

    return [_move_string(king_from, king_to)]


def _pawn_destinations(from_index: int, to_index: int, is_promotion: bool) -> list[Move]:
    if is_promotion:
        return [_move_string(from_index, to_index, promotion) for promotion in _PROMOTION_PIECES]
    return [_move_string(from_index, to_index)]


def _move_string(from_index: int, to_index: int, promotion: str | None = None) -> Move:
    move = index_to_algebraic(from_index) + index_to_algebraic(to_index)
    if promotion is not None:
        move += promotion
    return move
