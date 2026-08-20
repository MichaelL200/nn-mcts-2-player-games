import pygame
from ....core.interfaces import GameUI, Move
from ..board import ChessPiece, square_index, square_row_col, index_to_algebraic, algebraic_to_index
from ..state import ChessState, ChessPlayer
from ..game_logic import parse_move, is_in_check
from .display import ChessDisplay

_PROMOTION_PIECES = "qrbn"
_WHITE_PROMOTION_PIECE_BY_LETTER = {
    "q": ChessPiece.WHITE_QUEEN,
    "r": ChessPiece.WHITE_ROOK,
    "b": ChessPiece.WHITE_BISHOP,
    "n": ChessPiece.WHITE_KNIGHT,
}
_ANIMATION_STEPS = 16
_ANIMATION_FRAME_MS = 20  # time between frames in milliseconds


class ChessUI(GameUI):
    def __init__(self, width: int, height: int) -> None:
        pygame.init()
        self.display = ChessDisplay(width, height)
        self._selected_square: int | None = None
        self._last_move_squares: tuple[int, int] | None = None
        self._legal_destinations: frozenset[int] = frozenset()

    def render(self, state: ChessState) -> None:
        self.display.draw_board(
            state,
            selected_square=self._selected_square,
            last_move_squares=self._last_move_squares,
            check_square=self._check_square(state),
            legal_destinations=self._legal_destinations,
        )
        pygame.display.update()

    def get_player_move(self, state: ChessState, valid_moves: list[Move]) -> Move | None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                square = self.display.mouse_position_to_square(event.pos)
                if square is None:
                    continue

                if self._selected_square is None:
                    self._selected_square = square
                    self._legal_destinations = self._destinations_from(valid_moves, square)
                    continue

                candidates = self._moves_between(valid_moves, self._selected_square, square)
                self._selected_square = None
                self._legal_destinations = frozenset()

                # valid normal move
                if len(candidates) == 1:
                    return candidates[0]
                # promotion
                if len(candidates) > 1:
                    letter = self._ask_promotion_choice(state, state.active_player)
                    for move in candidates:
                        if move[4] == letter:
                            return move

        return None

    def animate_move(self, state: ChessState, move: Move) -> None:
        from_square, to_square, _ = parse_move(move)
        moving_piece = state.board.get_piece(from_square)

        sliding = [(from_square, to_square, moving_piece)]  # usually one (two for castling)
        hidden = {from_square, to_square}  # hide pieces on from and to squares (sometimes more)

        is_castling = (
            moving_piece in (ChessPiece.WHITE_KING, ChessPiece.BLACK_KING)
            and abs(to_square - from_square) == 2
        )
        if is_castling:
            row, _ = square_row_col(from_square)
            if to_square > from_square:
                rook_from, rook_to = square_index(row, 7), square_index(row, 5)
            else:
                rook_from, rook_to = square_index(row, 0), square_index(row, 3)
            rook_piece = state.board.get_piece(rook_from)
            sliding.append((rook_from, rook_to, rook_piece))
            hidden.update({rook_from, rook_to})

        is_en_passant = (
            moving_piece in (ChessPiece.WHITE_PAWN, ChessPiece.BLACK_PAWN)
            and state.board.get_piece(to_square) == ChessPiece.EMPTY
            and to_square % 8 != from_square % 8
        )
        if is_en_passant:
            captured_row, _ = square_row_col(from_square)
            _, captured_col = square_row_col(to_square)
            captured_square = square_index(captured_row, captured_col)
            hidden.add(captured_square)

        for step in range(1, _ANIMATION_STEPS + 1):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

            progress = step / _ANIMATION_STEPS
            self.display.draw_board(
                state,
                last_move_squares=self._last_move_squares,
                check_square=self._check_square(state),
                hidden_squares=frozenset(hidden),
            )
            for piece_from, piece_to, piece in sliding:
                from_row, from_col = square_row_col(piece_from)
                to_row, to_col = square_row_col(piece_to)
                start_x, start_y = self.display.square_center(from_row, from_col)
                end_x, end_y = self.display.square_center(to_row, to_col)
                x = start_x + (end_x - start_x) * progress
                y = start_y + (end_y - start_y) * progress
                self.display.draw_piece_at(piece, x, y)

            pygame.display.update()
            pygame.time.wait(_ANIMATION_FRAME_MS)

        self._last_move_squares = (from_square, to_square)

    def show_game_over(self, state: ChessState) -> bool:
        font = pygame.font.Font(None, 36)
        button_rect = pygame.Rect(
            self.display.width // 2 - 100,
            self.display.height // 2 - 50,
            200, 100,
        )
        button_color = (0, 128, 0)
        text_color = (255, 255, 255)
        text = font.render("Restart Game", True, text_color)
        text_rect = text.get_rect(center=button_rect.center)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        return True

            self.display.draw_board(state)
            pygame.draw.rect(self.display.screen, button_color, button_rect)
            self.display.screen.blit(text, text_rect)
            pygame.display.update()

    def quit(self) -> None:
        pygame.quit()

    def _check_square(self, state: ChessState) -> int | None:
        if not is_in_check(state):
            return None
        king = ChessPiece.WHITE_KING if state.active_player == ChessPlayer.WHITE else ChessPiece.BLACK_KING
        return state.board.squares.index(king)

    def _moves_between(self, valid_moves: list[Move], from_square: int, to_square: int) -> list[Move]:
        prefix = index_to_algebraic(from_square) + index_to_algebraic(to_square)
        return [move for move in valid_moves if move[:4] == prefix]

    def _destinations_from(self, valid_moves: list[Move], from_square: int) -> frozenset[int]:
        from_alg = index_to_algebraic(from_square)
        return frozenset(algebraic_to_index(move[2:4]) for move in valid_moves if move[:2] == from_alg)

    def _ask_promotion_choice(self, state: ChessState, color: ChessPlayer) -> str:
        pieces = [
            ChessPiece(_WHITE_PROMOTION_PIECE_BY_LETTER[letter] * (1 if color == ChessPlayer.WHITE else -1))
            for letter in _PROMOTION_PIECES
        ]
        box_width = self.display.square_size * len(pieces)
        box_height = self.display.square_size
        box_x = (self.display.width - box_width) // 2
        box_y = (self.display.height - box_height) // 2
        cell_rects = [
            pygame.Rect(box_x + i * self.display.square_size, box_y, self.display.square_size, self.display.square_size)
            for i in range(len(pieces))
        ]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for letter, rect in zip(_PROMOTION_PIECES, cell_rects):
                        if rect.collidepoint(event.pos):
                            return letter

            self.display.draw_board(state)
            pygame.draw.rect(self.display.screen, (245, 245, 245), (box_x, box_y, box_width, box_height))
            for rect, piece in zip(cell_rects, pieces):
                pygame.draw.rect(self.display.screen, (150, 150, 150), rect, 1)
                self.display.draw_piece_at(piece, rect.centerx, rect.centery)
            pygame.display.update()
