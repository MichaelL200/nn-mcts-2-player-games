import pygame
from importlib.resources import files
from ..board import ChessPiece
from ..state import ChessState

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
SELECTED_SQUARE = (246, 246, 105)
LAST_MOVE_SQUARE = (205, 210, 106)
CHECK_SQUARE = (231, 90, 90)
LEGAL_DESTINATION_MARKER = (60, 60, 60)

_FILES = "abcdefgh"

_ASSET_NAMES = {
    ChessPiece.WHITE_PAWN: "Chess_plt60.png",
    ChessPiece.WHITE_KNIGHT: "Chess_nlt60.png",
    ChessPiece.WHITE_BISHOP: "Chess_blt60.png",
    ChessPiece.WHITE_ROOK: "Chess_rlt60.png",
    ChessPiece.WHITE_QUEEN: "Chess_qlt60.png",
    ChessPiece.WHITE_KING: "Chess_klt60.png",
    ChessPiece.BLACK_PAWN: "Chess_pdt60.png",
    ChessPiece.BLACK_KNIGHT: "Chess_ndt60.png",
    ChessPiece.BLACK_BISHOP: "Chess_bdt60.png",
    ChessPiece.BLACK_ROOK: "Chess_rdt60.png",
    ChessPiece.BLACK_QUEEN: "Chess_qdt60.png",
    ChessPiece.BLACK_KING: "Chess_kdt60.png",
}


class ChessDisplay:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.square_size = min(self.width, self.height) // 8
        self.screen = self._init_screen(self.width, self.height)
        self.offset_x = (self.width - self.square_size * 8) // 2
        self.offset_y = (self.height - self.square_size * 8) // 2
        self._image_cache: dict[ChessPiece, pygame.Surface] = self._load_images()
        self._label_font = pygame.font.Font(None, max(14, self.square_size // 4))

    def _load_images(self) -> dict[ChessPiece, pygame.Surface]:
        size = (int(0.8 * self.square_size), int(0.8 * self.square_size))
        raw = {piece: self._load_image(name) for piece, name in _ASSET_NAMES.items()}
        return {piece: pygame.transform.scale(img, size) for piece, img in raw.items()}

    def _load_image(self, image_name: str) -> pygame.Surface:
        image_path = files(__package__) / "assets" / image_name
        return pygame.image.load(str(image_path))

    def _init_screen(self, width: int, height: int) -> pygame.Surface:
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        pygame.display.set_caption("Golemowe Szachy")
        return screen

    def draw_board(
        self,
        state: ChessState,
        selected_square: int | None = None,
        last_move_squares: tuple[int, int] | None = None,
        check_square: int | None = None,
        hidden_squares: frozenset[int] = frozenset(),
        legal_destinations: frozenset[int] = frozenset(),
    ) -> None:
        self.screen.fill((30, 30, 30))
        squares = state.board.squares

        for row in range(8):
            for col in range(8):
                index = row * 8 + col
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                if index == check_square:
                    color = CHECK_SQUARE
                elif index == selected_square:
                    color = SELECTED_SQUARE
                elif last_move_squares is not None and index in last_move_squares:
                    color = LAST_MOVE_SQUARE

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        self.offset_x + col * self.square_size,
                        self.offset_y + row * self.square_size,
                        self.square_size,
                        self.square_size,
                    ),
                )

                occupied = index not in hidden_squares and squares[index] != ChessPiece.EMPTY
                if index in legal_destinations:
                    self._draw_move_marker(row, col, occupied)

                if occupied:
                    x, y = self.square_center(row, col)
                    self.draw_piece_at(squares[index], x, y)

        self._draw_labels()

    def _draw_move_marker(self, row: int, col: int, occupied: bool) -> None:
        x, y = self.square_center(row, col)
        if occupied:
            radius = int(self.square_size * 0.47)
            width = max(2, self.square_size // 20)
            pygame.draw.circle(self.screen, LEGAL_DESTINATION_MARKER, (x, y), radius, width)
        else:
            radius = int(self.square_size * 0.15)
            pygame.draw.circle(self.screen, LEGAL_DESTINATION_MARKER, (x, y), radius)

    def mouse_position_to_square(self, pos: tuple[int, int]) -> int | None:
        x, y = pos
        col = (x - self.offset_x) // self.square_size
        row = (y - self.offset_y) // self.square_size
        if 0 <= row < 8 and 0 <= col < 8:
            return row * 8 + col
        return None

    def square_center(self, row: int, col: int) -> tuple[int, int]:
        x = self.offset_x + col * self.square_size + self.square_size // 2
        y = self.offset_y + row * self.square_size + self.square_size // 2
        return x, y

    def draw_piece_at(self, piece: ChessPiece, x: float, y: float) -> None:
        img = self._get_piece_image(piece)
        rect = img.get_rect(center=(x, y))
        self.screen.blit(img, rect)

    def _draw_labels(self) -> None:
        label_color = (50, 50, 50)
        for col in range(8):
            label = self._label_font.render(_FILES[col], True, label_color)
            x = self.offset_x + col * self.square_size + 2
            y = self.offset_y + 8 * self.square_size - label.get_height() - 2
            self.screen.blit(label, (x, y))
        for row in range(8):
            label = self._label_font.render(str(8 - row), True, label_color)
            x = self.offset_x + 8 * self.square_size - label.get_width() - 2
            y = self.offset_y + row * self.square_size + 2
            self.screen.blit(label, (x, y))

    def _get_piece_image(self, piece: ChessPiece) -> pygame.Surface:
        return self._image_cache[piece]
