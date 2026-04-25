import pygame
import pkg_resources
from ..board import CheckersPiece
from ..state import CheckersState


class Display:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.square_size = min(self.width, self.height) // 8
        self.highlighted_square = None
        self.screen = self._init_screen(self.width, self.height)
        self.offset_x = (self.width - self.square_size * 8) // 2
        self.offset_y = (self.height - self.square_size * 8) // 2
        self._image_cache: dict[CheckersPiece, pygame.Surface] = self._load_images()

    def _load_images(self) -> dict[CheckersPiece, pygame.Surface]:
        raw = {
            CheckersPiece.BLACK:       self._load_image("black_piece.png"),
            CheckersPiece.WHITE:       self._load_image("white_piece.png"),
            CheckersPiece.BLACK_QUEEN: self._load_image("black_queen.png"),
            CheckersPiece.WHITE_QUEEN: self._load_image("white_queen.png"),
        }
        size = (int(0.75 * self.square_size), int(0.75 * self.square_size))
        return {piece: pygame.transform.scale(img, size) for piece, img in raw.items()}

    def _load_image(self, image_name: str) -> pygame.Surface:
        image_path = pkg_resources.resource_filename(__name__, f"assets/{image_name}")
        return pygame.image.load(image_path)

    def _get_piece_image(self, piece: CheckersPiece) -> pygame.Surface | None:
        return self._image_cache.get(piece)

    def draw_board(self, state: CheckersState) -> None:
        self.screen.fill((230, 230, 230))
        pieces = state.get_board().get_squares()

        for j in range(8):
            for i in range(8):
                if (i, j) == self.highlighted_square:
                    color = (255, 0, 0)
                else:
                    color = (255, 255, 255) if (i + j) % 2 != 0 else (0, 0, 0)

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
                    indx = j * 4 + i // 2
                    piece = pieces[indx]
                    if piece != CheckersPiece.EMPTY:
                        img = self._get_piece_image(piece)
                        img = pygame.transform.scale(
                            img, (0.75 * self.square_size,
                                  0.75 * self.square_size)
                        )
                        x_pad, y_pad = self._calculate_padding(
                            self.square_size, self.square_size)
                        self.screen.blit(
                            img,
                            (
                                self.offset_x + i * self.square_size + x_pad,
                                self.offset_y + j * self.square_size + y_pad,
                            ),
                        )

    def highlight_square(self, cords: tuple[int, int]):
        self.highlighted_square = cords

    def _init_screen(self, width: int, height: int) -> pygame.Surface:
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        pygame.display.set_caption("Golemowe Warcaby")
        return screen

    def _calculate_padding(self, new_width: int, new_height: int) -> tuple[int, int]:
        target_width = int(0.75 * self.square_size)
        target_height = int(0.75 * self.square_size)
        x_pad = (self.square_size - target_width) // 2
        y_pad = (self.square_size - target_height) // 2
        return x_pad, y_pad
