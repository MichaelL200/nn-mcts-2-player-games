import numpy as np
from copy import deepcopy

from .encoder import CheckersEncoder
from .board import CheckersPiece, CheckersBoard
from .state import CheckersPlayer, CheckersState
from ...core.interfaces import GameSimulation, Move


class Checkers(GameSimulation):
    def __init__(self):
        self._encoder = CheckersEncoder()

    @property
    def encoder(self) -> CheckersEncoder:
        return self._encoder
    

    def get_starting_state(self) -> CheckersState:
        """"
        State with white player to move, deafult board of 64-element 1D array."
        """
        active_player = CheckersPlayer.WHITE
        board = CheckersBoard(np.array([
            CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK,
            CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK,
            CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK, CheckersPiece.BLACK,
            CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
            CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
            CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE,
            CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE,
            CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE, CheckersPiece.WHITE,
        ]).flatten())
        return CheckersState(board, active_player)

    def get_moves(self, game_state: CheckersState) -> list[Move]:
        """
        Returns a list of all possible moves for the current player.
        """
        capture_moves = self._capture_moves(game_state)

        if len(capture_moves) > 0:
            return capture_moves

        return self._standard_moves(game_state)

    def make_random_move(self, game_state: CheckersState) -> CheckersState:
        """
        Returns a new game state after making a random move.
        """
        random_move = np.random.choice(self.get_moves(game_state))
        return self.make_move(game_state, random_move)

    def is_terminal(self, game_state: CheckersState) -> bool:
        """
        Returns True if the game is over, False otherwise.
        """
        white_absent, black_absent = True, True

        for slot in game_state.board.squares:
            if slot == CheckersPiece.WHITE or slot == CheckersPiece.WHITE_QUEEN:
                white_absent = False
            elif slot == CheckersPiece.BLACK or slot == CheckersPiece.BLACK_QUEEN:
                black_absent = False

        return white_absent or black_absent or self._is_draw(game_state)

    def reward(self, game_state: CheckersState, player: CheckersPlayer) -> int:
        """
        Returns the reward for the game with white player as the maximizing player.
        """
        if self._is_draw(game_state):
            return 0

        mod = 1 if player == CheckersPlayer.WHITE else -1

        for slot in game_state.get_board().get_squares():
            if slot in self._pieces_from_player(CheckersPlayer.WHITE):
                return 1 * mod
            elif slot in self._pieces_from_player(CheckersPlayer.BLACK):
                return -1 * mod

    def _is_draw(self, game_state: CheckersState) -> bool:
        avaible_moves = self.get_moves(game_state)
        avaible_pieces = self._check_piece(game_state, game_state.get_player())

        if len(avaible_moves) == 0:
            if avaible_pieces:
                return True
            return False
        return False

    def _check_piece(self, game_state: CheckersState, owner: CheckersPlayer) -> bool:
        for slot in game_state.get_board().get_squares():
            if slot in self._pieces_from_player(owner):
                return True
        return False

    def _standard_moves(self, game_state:  CheckersState) -> list[Move]:
        player = game_state.get_player()
        board = game_state.get_board()

        moves = []
        for index, slot in enumerate(board.squares):

            if slot == CheckersPiece.WHITE and player == CheckersPlayer.WHITE:
                tl_index, tr_index = game_state.board._get_left_up(
                    index), game_state.board._get_right_up(index)
                if tl_index is not None and game_state.board.get_piece(tl_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tl_index))
                if tr_index is not None and game_state.board.get_piece(tr_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tr_index))

            elif slot == CheckersPiece.BLACK and player == CheckersPlayer.BLACK:
                tl_index, tr_index = game_state.board._get_left_down(
                    index), game_state.board._get_right_down(index)
                if tr_index is not None and game_state.board.get_piece(tr_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tr_index))
                if tl_index is not None and game_state.board.get_piece(tl_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tl_index))

            elif ((slot == CheckersPiece.WHITE_QUEEN and player == CheckersPlayer.WHITE)
                  or (slot == CheckersPiece.BLACK_QUEEN and player == CheckersPlayer.BLACK)
                  ):
                movables = game_state.board.get_all_free_indexes(index)
                for new_index in movables:
                    moves.append(str(index)+"-"+str(new_index))

        return moves

    def _capture_moves(self, game_state: CheckersState) -> list[Move]:
        player = game_state.get_player()
        board = game_state.get_board()

        moves = []
        for index, slot in enumerate(board.squares):
            if slot in self._pieces_from_player(player, opposite=False):
                moves += self._captures_for_square(game_state,
                                                   index, str(index))

        return moves

    def _captures_for_square(self, game_state: CheckersState, index: int, move_string: str) -> list[Move]:
        all_moves = []
        piece = game_state.board.get_piece(index)

        # Differentiating between normal pieces and queens
        if piece in (CheckersPiece.WHITE, CheckersPiece.BLACK):
            neighbour_indexes = game_state.board.get_closest_indexes(index)
        elif piece in (CheckersPiece.WHITE_QUEEN, CheckersPiece.BLACK_QUEEN):
            neighbour_indexes = game_state.board.get_closest_occupied_indexes(
                index)

        for direction_id, neighbour_index in enumerate(neighbour_indexes):
            # Check neighbour for oponent piece
            if neighbour_index is None:
                continue
            neighbour_piece = game_state.board.get_piece(neighbour_index)
            if neighbour_piece not in self._pieces_from_piece(piece, opposite=True):
                continue

            # Check tile behind oponent piece
            new_index = game_state.board.get_closest_index(
                neighbour_index, direction_id)
            if new_index is None:
                continue
            if game_state.board.get_piece(new_index) != CheckersPiece.EMPTY:
                continue

            # Perform move & repeat
            # move leading from initial state
            whole_move = move_string + "x" + str(new_index)
            # move leading from current state
            new_move = str(index) + "x" + str(new_index)
            new_state = self.make_move(deepcopy(game_state), new_move)
            all_moves += self._captures_for_square(
                new_state, new_index, whole_move)

        if len(all_moves) == 0 and 'x' in move_string:
            return [move_string]
        return all_moves

    @staticmethod
    def _pieces_from_piece(piece: CheckersPiece, opposite: bool = False) -> tuple[CheckersPiece, CheckersPiece]:
        white_pieces = (CheckersPiece.WHITE, CheckersPiece.WHITE_QUEEN)
        black_pieces = (CheckersPiece.BLACK, CheckersPiece.BLACK_QUEEN)

        if piece in white_pieces:
            if opposite:
                return black_pieces
            return white_pieces

        elif piece in black_pieces:
            if opposite:
                return white_pieces
            return black_pieces

    @staticmethod
    def _pieces_from_player(player: CheckersPlayer, opposite: bool = False) -> tuple[CheckersPiece, CheckersPiece]:
        white_pieces = (CheckersPiece.WHITE, CheckersPiece.WHITE_QUEEN)
        black_pieces = (CheckersPiece.BLACK, CheckersPiece.BLACK_QUEEN)

        if player == CheckersPlayer.WHITE:
            if opposite:
                return black_pieces
            return white_pieces

        elif player == CheckersPlayer.BLACK:
            if opposite:
                return white_pieces
            return black_pieces

    def make_move(self, game_state: CheckersState, move: Move) -> CheckersState:
        """
        Performs move on given state and returns new one.
        Works only for valid moves.
        """
        promotion_fields = [0, 1, 2, 3]
        queen_piece = CheckersPiece.WHITE_QUEEN
        if game_state.get_player() == CheckersPlayer.BLACK:
            queen_piece = CheckersPiece.BLACK_QUEEN
            promotion_fields = [28, 29, 30, 31]

        # No capture
        if 'x' not in move:
            move_fields = move.split('-')
            start_field_idx, final_field_idx = tuple(
                map(lambda x: int(x), move_fields))
            start_piece = game_state.board.get_piece(start_field_idx)

        # Capture
        else:
            move_fields = move.split('x')
            start_field_idx, * \
                mid_fields_idx, final_field_idx = tuple(
                    map(lambda x: int(x), move_fields))
            start_piece = game_state.board.get_piece(start_field_idx)
            fields_inbetween = []
            for i in range(len(move_fields)-1):
                fields_inbetween += self._get_inbetween_fields(
                    game_state, int(move_fields[i]), int(move_fields[i+1]))
            for field in fields_inbetween:
                game_state.board.set_piece(field, CheckersPiece.EMPTY)

        # Set new piece
        game_state.board.set_piece(start_field_idx, CheckersPiece.EMPTY)
        if final_field_idx in promotion_fields:
            game_state.board.set_piece(final_field_idx, queen_piece)
        else:
            game_state.board.set_piece(final_field_idx, start_piece)

        # Switch player
        game_state = self._switch_player(game_state)

        return game_state

    def _get_inbetween_fields(self, state: CheckersState, start_field: int, final_field: int) -> int:
        for dir_pair in [[0, 3], [3, 0], [1, 2], [2, 1]]:
            dir1, dir2 = dir_pair[0], dir_pair[1]
            diagonal = state.board._get_diagonal(start_field, dir1)
            if final_field in diagonal:
                opposite_diagonal = state.board._get_diagonal(
                    final_field, dir2)
                return [field for field in opposite_diagonal if field in diagonal]

    def _switch_player(self, state: CheckersState):
        if state.get_player() == CheckersPlayer.WHITE:
            state.active_player = CheckersPlayer.BLACK
        else:
            state.active_player = CheckersPlayer.WHITE
        return state
