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


def is_checkmate(state: ChessState) -> bool:
    return is_in_check(state) and not generate_legal_moves(state)


def is_stalemate(state: ChessState) -> bool:
    return not is_in_check(state) and not generate_legal_moves(state)


def is_in_check(state: ChessState) -> bool:
    return _king_in_check(state.board, state.active_player)


def generate_legal_moves(state: ChessState) -> list[Move]:
    color = state.active_player
    legal_moves = []
    for move in generate_pseudo_legal_moves(state):
        board_after = apply_move(state.board, move)
        if not _king_in_check(board_after, color):
            legal_moves.append(move)
    return legal_moves


def apply_move(board: ChessBoard, move: Move) -> ChessBoard:
    from_square, to_square, promotion = parse_move(move)
    squares = board.squares.copy()
    moving_piece = squares[from_square]
    squares[from_square] = ChessPiece.EMPTY
    squares[to_square] = _promoted_piece(promotion, piece_color(moving_piece)) if promotion else moving_piece
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
    return moves


def is_square_attacked(board: ChessBoard, square: int, by_color: ChessPlayer) -> bool:
    for index, piece in enumerate(board.squares):
        if piece == ChessPiece.EMPTY or piece_color(piece) != by_color:
            continue
        match piece:
            case ChessPiece.WHITE_PAWN | ChessPiece.BLACK_PAWN:
                targets = _pawn_attack_targets(index, by_color)
            case ChessPiece.WHITE_KNIGHT | ChessPiece.BLACK_KNIGHT:
                targets = _leaper_targets(index, _KNIGHT_OFFSETS)
            case ChessPiece.WHITE_BISHOP | ChessPiece.BLACK_BISHOP:
                targets = _slider_targets(board, index, _BISHOP_DIRECTIONS)
            case ChessPiece.WHITE_ROOK | ChessPiece.BLACK_ROOK:
                targets = _slider_targets(board, index, _ROOK_DIRECTIONS)
            case ChessPiece.WHITE_QUEEN | ChessPiece.BLACK_QUEEN:
                targets = _slider_targets(board, index, _QUEEN_DIRECTIONS)
            case ChessPiece.WHITE_KING | ChessPiece.BLACK_KING:
                targets = _leaper_targets(index, _KING_OFFSETS)
            case _:
                continue
        if square in targets:
            return True
    return False


def _king_in_check(board: ChessBoard, color: ChessPlayer) -> bool:
    king_square = _king_square(board, color)
    return is_square_attacked(board, king_square, _enemy_color(color))


def _promoted_piece(promotion: str, color: ChessPlayer) -> ChessPiece:
    white_piece = _WHITE_PROMOTION_PIECE_BY_LETTER[promotion]
    return white_piece if color == ChessPlayer.WHITE else ChessPiece(-white_piece)


def _king_square(board: ChessBoard, color: ChessPlayer) -> int:
    king = ChessPiece.WHITE_KING if color == ChessPlayer.WHITE else ChessPiece.BLACK_KING
    return board.squares.index(king)


def _enemy_color(color: ChessPlayer) -> ChessPlayer:
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


def _pawn_attack_targets(index: int, color: ChessPlayer) -> list[int]:
    row, col = square_row_col(index)
    direction = -1 if color == ChessPlayer.WHITE else 1
    target_row = row + direction
    targets = []
    if 0 <= target_row < 8:
        for d_col in (-1, 1):
            target_col = col + d_col
            if 0 <= target_col < 8:
                targets.append(square_index(target_row, target_col))
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

    return moves


def _pawn_destinations(from_index: int, to_index: int, is_promotion: bool) -> list[Move]:
    if is_promotion:
        return [_move_string(from_index, to_index, promotion) for promotion in _PROMOTION_PIECES]
    return [_move_string(from_index, to_index)]


def _move_string(from_index: int, to_index: int, promotion: str | None = None) -> Move:
    move = index_to_algebraic(from_index) + index_to_algebraic(to_index)
    if promotion is not None:
        move += promotion
    return move
