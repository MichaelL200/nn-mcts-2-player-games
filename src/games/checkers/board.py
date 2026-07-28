from enum import Enum
from ...core.interfaces import Board


class CheckersPiece(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = -1
    WHITE_QUEEN = 2
    BLACK_QUEEN = -2


class CheckersBoard(Board):
    BOARD_SIZE = 10
    SQUARES_PER_ROW = BOARD_SIZE // 2
    PLAYABLE_SQUARES = BOARD_SIZE * BOARD_SIZE // 2

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
        row = indx // CheckersBoard.SQUARES_PER_ROW
        if row == 0:
            return None
        return CheckersBoard._coord_to_index(row - 1, CheckersBoard._index_to_board_col(indx) - 1)

    @staticmethod
    def _get_right_up(indx: int) -> int | None:
        row = indx // CheckersBoard.SQUARES_PER_ROW
        if row == 0:
            return None
        return CheckersBoard._coord_to_index(row - 1, CheckersBoard._index_to_board_col(indx) + 1)

    @staticmethod
    def _get_left_down(indx: int) -> int | None:
        row = indx // CheckersBoard.SQUARES_PER_ROW
        if row == CheckersBoard.BOARD_SIZE - 1:
            return None
        return CheckersBoard._coord_to_index(row + 1, CheckersBoard._index_to_board_col(indx) - 1)

    @staticmethod
    def _get_right_down(indx: int) -> int | None:
        row = indx // CheckersBoard.SQUARES_PER_ROW
        if row == CheckersBoard.BOARD_SIZE - 1:
            return None
        return CheckersBoard._coord_to_index(row + 1, CheckersBoard._index_to_board_col(indx) + 1)

    @staticmethod
    def _index_to_board_col(indx: int) -> int:
        row, col = divmod(indx, CheckersBoard.SQUARES_PER_ROW)
        return col * 2 + (1 if row % 2 == 0 else 0)

    @staticmethod
    def _coord_to_index(row: int, board_col: int) -> int | None:
        if row < 0 or row >= CheckersBoard.BOARD_SIZE:
            return None
        if board_col < 0 or board_col >= CheckersBoard.BOARD_SIZE:
            return None
        if row % 2 == 0:
            if board_col % 2 != 1:
                return None
            return row * CheckersBoard.SQUARES_PER_ROW + board_col // 2
        if board_col % 2 != 0:
            return None
        return row * CheckersBoard.SQUARES_PER_ROW + board_col // 2

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
        top = " ┌───" + (CheckersBoard.BOARD_SIZE - 1) * "┬───" + "┐\n"
        mid = " ├───" + (CheckersBoard.BOARD_SIZE - 1) * "┼───" + "┤\n"
        bot = " └───" + (CheckersBoard.BOARD_SIZE - 1) * "┴───" + "┘\n"

        string = top
        for i in range(CheckersBoard.BOARD_SIZE):
            row = " │"
            for j in range(CheckersBoard.BOARD_SIZE):
                if (i + j) % 2 == 0:
                    piece = CheckersPiece.EMPTY
                else:
                    piece = self.squares[i * CheckersBoard.SQUARES_PER_ROW + j // 2]

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
            if i != CheckersBoard.BOARD_SIZE - 1:
                string += mid
        string += bot
        return string
