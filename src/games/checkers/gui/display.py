from pathlib import Path
import pygame
from ..board import CheckersPiece
from ..state import CheckersState
from pygame._sdl2.video import Window


class Display:

    PIECE_SCALE = 0.75

    def __init__(self, width: int, height: int):
        self.board_size = 10
        self.highlighted_squares = {}

        self.window = Window("nn-mcts-2-player-games", size=(width, height), resizable=True)
        self.window.maximize()
        self.update_dimensions()
        self._setup_icon()

    def draw_board(self, state: CheckersState) -> None:
        self.screen.fill((230, 230, 230))
        pieces = state.get_board().get_squares()
        x_pad, y_pad = self._calculate_padding()

        for j in range(self.board_size):
            for i in range(self.board_size):
                color = self.highlighted_squares.get(
                    (i, j),
                    (0, 0, 0) if (i + j) % 2 != 0 else (255, 255, 255),
                )

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        self.offset_x + i * self.square_size,
                        self.offset_y + j * self.square_size,
                        self.square_size,
                        self.square_size,
                    ),
                )

                if i % 2 != j % 2:
                    indx = j * (self.board_size // 2) + i // 2
                    piece = pieces[indx]
                    if piece != CheckersPiece.EMPTY:
                        img = self._get_piece_image(piece)
                        if img:
                            self.screen.blit(
                                img,
                                (
                                    self.offset_x + i * self.square_size + x_pad,
                                    self.offset_y + j * self.square_size + y_pad,
                                ),
                            )

    def highlight_squares(self, squares: dict[tuple[int, int], tuple[int, int, int]]) -> None:
        self.highlighted_squares = squares

    def update_dimensions(self) -> None:
        self.screen = self.window.get_surface()
        self.width, self.height = self.screen.get_size()
        self.square_size = min(self.width, self.height) // self.board_size
        self.offset_x = (self.width - self.square_size * self.board_size) // 2
        self.offset_y = (self.height - self.square_size * self.board_size) // 2
        self._image_cache = self._load_images()

    def _setup_icon(self) -> None:
        icon_path = Path(__file__).resolve().parent / "assets" / "black_queen.png"
        raw_icon = pygame.image.load(str(icon_path)).convert_alpha()
        icon_size = raw_icon.get_size()

        icon_surface = pygame.Surface(icon_size, pygame.SRCALPHA)
        center = (icon_size[0] // 2, icon_size[1] // 2)
        radius = min(center)
        pygame.draw.circle(icon_surface, (255, 255, 255), center, radius)

        scaled_size = (int(icon_size[0] * 0.7), int(icon_size[1] * 0.7))
        scaled_icon = pygame.transform.smoothscale(raw_icon, scaled_size)
        icon_rect = scaled_icon.get_rect(center=center)
        icon_surface.blit(scaled_icon, icon_rect)

        self.window.set_icon(icon_surface)

    def _load_images(self) -> dict[CheckersPiece, pygame.Surface]:
        raw = {
            CheckersPiece.BLACK:       self._load_image("black_piece.png"),
            CheckersPiece.WHITE:       self._load_image("white_piece.png"),
            CheckersPiece.BLACK_QUEEN: self._load_image("black_queen.png"),
            CheckersPiece.WHITE_QUEEN: self._load_image("white_queen.png"),
        }
        target_size = int(self.PIECE_SCALE * self.square_size)
        size = (target_size, target_size)
        return {piece: pygame.transform.scale(img, size) for piece, img in raw.items()}

    def _load_image(self, image_name: str) -> pygame.Surface:
        image_path = Path(__file__).resolve().parent / "assets" / image_name
        return pygame.image.load(str(image_path))

    def _get_piece_image(self, piece: CheckersPiece) -> pygame.Surface | None:
        return self._image_cache.get(piece)

    def _calculate_padding(self) -> tuple[int, int]:
        target_size = int(self.PIECE_SCALE * self.square_size)
        pad = (self.square_size - target_size) // 2
        return pad, pad
