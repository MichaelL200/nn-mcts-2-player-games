import pygame
from copy import deepcopy
from ....core.interfaces import GameUI, Move
from ..board import CheckersPiece
from ..state import CheckersState
from .display import Display


class CheckersUI(GameUI):
    def __init__(self, width: int, height: int) -> None:
        pygame.init()
        self.display = Display(width, height)
        self._xy_selected = None
        self._selected_color = (80, 140, 255)
        self._capture_source_color = (255, 180, 60)
        self._legal_move_color = (90, 200, 90)
        self._capture_move_color = (220, 80, 80)

    def render(self, state: CheckersState) -> None:
        self.display.draw_board(state)
        pygame.display.update()

    def get_player_move(self, state: CheckersState, valid_moves: list[Move]) -> Move | None:
        valid_coords = self._convert_moves(valid_moves)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN:
                xy_new = self._mouse_position_to_board_position(pygame.mouse.get_pos())

                if self._xy_selected is not None:
                    move_candidate = (self._xy_selected, xy_new)
                    self.display.highlight_squares({})
                    self._xy_selected = None

                    if move_candidate in valid_coords:
                        move_str = valid_moves[valid_coords.index(move_candidate)]
                        return move_str
                else:
                    highlight_map = self._build_highlight_map(xy_new, valid_moves, valid_coords)
                    self.display.highlight_squares(highlight_map)
                    self._xy_selected = xy_new

        return None

    def animate_move(self, state: CheckersState, move: Move) -> None:
        squares = move.split("x") if "x" in move else move.split("-")
        sub_moves = [
            (int(squares[i]), int(squares[i + 1]))
            for i in range(len(squares) - 1)
        ]
        fake_state = deepcopy(state)
        fake_board = fake_state.board.get_squares().copy()

        for start, end in sub_moves:
            fake_state.board.squares = fake_board
            inbetween = self._get_inbetween_fields(fake_state, start, end)

            fake_board[end] = fake_board[start]
            fake_board[start] = CheckersPiece.EMPTY
            for square in inbetween:
                fake_board[square] = CheckersPiece.EMPTY
            self.display.draw_board(fake_state)
            pygame.display.update()
            pygame.time.wait(500)

    def show_game_over(self, state: CheckersState) -> bool:
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

    def _mouse_position_to_board_position(self, pos: tuple[int, int]) -> tuple[int, int]:
        x, y = pos
        x = (x - self.display.offset_x) // self.display.square_size
        y = (y - self.display.offset_y) // self.display.square_size
        return x, y

    @staticmethod
    def _idx50_to_10x10coords(idx: int) -> tuple[int, int]:
        y = idx // 5
        x = (idx % 5) * 2 + (y % 2 == 0)
        return x, y

    def _convert_moves(self, moves_str: list[Move]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        converted = []
        for move_str in moves_str:
            parts = move_str.split("x") if "x" in move_str else move_str.split("-")
            start = self._idx50_to_10x10coords(int(parts[0]))
            end = self._idx50_to_10x10coords(int(parts[-1]))
            converted.append((start, end))
        return converted

    def _get_inbetween_fields(self, state: CheckersState, start_field: int, final_field: int) -> list[int]:
        for dir_pair in [[0, 3], [3, 0], [1, 2], [2, 1]]:
            dir1, dir2 = dir_pair
            diagonal = state.board._get_diagonal(start_field, dir1)
            if final_field in diagonal:
                opposite_diagonal = state.board._get_diagonal(final_field, dir2)
                return [f for f in opposite_diagonal if f in diagonal]
        return []

    def _build_highlight_map(
        self,
        source_xy: tuple[int, int],
        valid_moves: list[Move],
        valid_coords: list[tuple[tuple[int, int], tuple[int, int]]],
    ) -> dict[tuple[int, int], tuple[int, int, int]]:
        source_moves = [
            (move_str, start, end)
            for move_str, (start, end)
            in zip(valid_moves, valid_coords)
            if start == source_xy
        ]

        if not source_moves:
            capture_sources = {
                start
                for move_str, (start, _)
                in zip(valid_moves, valid_coords)
                if "x" in move_str
            }
            highlights = {source_xy: self._selected_color}
            for square in capture_sources:
                if square != source_xy:
                    highlights[square] = self._capture_source_color
            return highlights

        highlights = {source_xy: self._selected_color}

        for move_str, _, end in source_moves:
            if "x" in move_str:
                highlights[end] = self._capture_move_color
            else:
                highlights[end] = self._legal_move_color

        return highlights
