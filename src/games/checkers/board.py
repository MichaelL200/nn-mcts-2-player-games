from enum import Enum
from ...core import GameState


class CheckersPiece(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = -1
    WHITE_QUEEN = 2
    BLACK_QUEEN = -2


class CheckersBoard(GameState):
    def __init__(self, squares):
        self.squares = squares

    def get_squares(self) -> list[CheckersPiece]:
        """
        Returns the squares of the board.
        """
        return self.squares

    def get_piece(self, index: int) -> CheckersPiece:
        """
        Get the piece at the given index.
        """
        return self.squares[index]

    def set_piece(self, index: int, piece: CheckersPiece):
        """
        Set the piece at the given index.
        """
        self.squares[index] = piece

    def get_closest_index(self, indx, direction_id: int) -> list[int | None]:
        """
        1 = TL, 2 = TR, 3 = BL, 4 = BR
        """
        # Didn't bother with enum :3
        if direction_id == 0:  # TL
            return self._get_left_up(indx)
        elif direction_id == 1:  # TR
            return self._get_right_up(indx)
        elif direction_id == 2:  # BL
            return self._get_left_down(indx)
        elif direction_id == 3:  # BR
            return self._get_right_down(indx)

    def get_closest_indexes(self, indx: int) -> list[int | None]:
        """
        Retuns the indexes of four diagonal neighbors,
        or Nones in case some are out of bounds.
        """
        return [
            self._get_left_up(indx),
            self._get_right_up(indx),
            self._get_left_down(indx),
            self._get_right_down(indx),
        ]

    def get_closest_occupied_indexes(self, indx: int) -> list[int]:
        """
        Returns the indexes of the closest occupied
        diagonal squares of the given index.
        """
        all_indxs = []
        for new_indx, direction_id in zip(self.get_closest_indexes(indx), range(4)):

            while (
                new_indx is not None and self.squares[new_indx] == CheckersPiece.EMPTY
            ):
                new_indx = self.get_closest_index(new_indx, direction_id)

            all_indxs.append(new_indx)
        return all_indxs

    def get_all_free_indexes(
        self,
        indx,
    ) -> list[int]:
        """
        Returns all the indexes of the free diagonal
        squares of the given index.
        """
        all_indxs = []
        for new_indx, direction_id in zip(self.get_closest_indexes(indx), range(4)):

            while (
                new_indx is not None and self.get_piece(
                    new_indx) == CheckersPiece.EMPTY
            ):
                all_indxs.append(new_indx)
                new_indx = self.get_closest_index(new_indx, direction_id)

        return all_indxs

    @staticmethod
    def _get_left_up(indx: int) -> int | None:
        row = int(indx / 4)
        if indx % 8 == 4 or indx <= 3:
            return None
        elif row % 2 == 0:
            return indx - 4
        else:
            return indx - 5

    @staticmethod
    def _get_right_up(indx: int) -> int | None:
        row = int(indx / 4)
        if indx % 8 == 3 or indx <= 3:
            return None
        elif row % 2 == 0:
            return indx - 3
        else:
            return indx - 4

    @staticmethod
    def _get_left_down(indx: int) -> int | None:
        row = int(indx / 4)
        if indx % 8 == 4 or indx >= 28:
            return None
        elif row % 2 == 0:
            return indx + 4
        else:
            return indx + 3

    @staticmethod
    def _get_right_down(indx: int) -> int | None:
        row = int(indx / 4)
        if indx % 8 == 3 or indx >= 28:
            return None
        elif row % 2 == 0:
            return indx + 5
        else:
            return indx + 4

    def _get_diagonal(self, indx: int, direction_id: int) -> list[int]:
        """
        Returns the indexes of the diagonal squares
        in the given direction.
        """
        all_indxs = []
        new_indx = self.get_closest_index(indx, direction_id)
        while new_indx is not None:
            all_indxs.append(new_indx)
            new_indx = self.get_closest_index(new_indx, direction_id)
        return all_indxs

    def __str__(self):
        empty = "   "
        white = " ⛂ "
        white_queen = " ⛃ "
        black = " ⛀ "
        black_queen = " ⛁ "
        top = " ┌───" + 7 * "┬───" + "┐\n"
        mid = " ├───" + 7 * "┼───" + "┤\n"
        bot = " └───" + 7 * "┴───" + "┘\n"

        string = top
        for i in range(8):
            row = " │"
            for j in range(8):
                if i % 2 == 0:
                    if j % 2 == 1:
                        piece = self.squares[int(i * 4) + int(j / 2)]
                    else:
                        piece = CheckersPiece.EMPTY
                else:
                    if j % 2 == 0:
                        piece = self.squares[int(i * 4) + int(j / 2)]
                    else:
                        piece = CheckersPiece.EMPTY

                if piece == CheckersPiece.EMPTY:
                    row += empty
                elif piece == CheckersPiece.WHITE:
                    row += white
                elif piece == CheckersPiece.BLACK:
                    row += black
                elif piece == CheckersPiece.WHITE_QUEEN:
                    row += white_queen
                elif piece == CheckersPiece.BLACK_QUEEN:
                    row += black_queen
                row += "│"

            string += row + "\n"
            if i != 7:
                string += mid
        string += bot
        return string
