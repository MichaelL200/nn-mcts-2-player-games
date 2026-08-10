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
        State with white player to move, default 10x10 board.
        """
        active_player = CheckersPlayer.WHITE
        squares = (
            [CheckersPiece.BLACK] * 20
            + [CheckersPiece.EMPTY] * 10
            + [CheckersPiece.WHITE] * 20
        )
        board = CheckersBoard(np.array(squares))
        state = CheckersState(board, active_player)

        position_key = (tuple(state.board.squares), state.active_player)
        state.position_history[position_key] = 1

        return state

    def get_moves(self, game_state: CheckersState) -> list[Move]:
        """
        Returns a list of all possible moves for the current player.
        """
        capture_moves = self._capture_moves(game_state)

        if len(capture_moves) > 0:
            max_captures = max(move.count('x') for move in capture_moves)
            return [move for move in capture_moves if move.count('x') == max_captures]

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

        if len(self.get_moves(game_state)) == 0:
            return True
        return white_absent or black_absent or self._is_draw(game_state)

    def reward(self, game_state: CheckersState, player: CheckersPlayer) -> int:
        """
        Returns the reward for the game with white player as the maximizing player.
        """
        white_has_pawns, black_has_pawns = False, False

        for slot in game_state.board.squares:
            if slot == CheckersPiece.WHITE or slot == CheckersPiece.WHITE_QUEEN:
                white_has_pawns = True
            elif slot == CheckersPiece.BLACK or slot == CheckersPiece.BLACK_QUEEN:
                black_has_pawns = True
        if white_has_pawns and not black_has_pawns:
            return CheckersPlayer.WHITE.value
        elif black_has_pawns and not white_has_pawns:
            return CheckersPlayer.BLACK.value

        if len(self.get_moves(game_state)) == 0:
            loser = game_state.get_player()
            return CheckersPlayer.BLACK.value if loser == CheckersPlayer.WHITE else CheckersPlayer.WHITE.value

        return 0

    def _is_draw(self, game_state: CheckersState) -> bool:

        # 3-fold repetition: same position, same side to move, 3rd time.
        position_key = (tuple(game_state.board.squares), game_state.active_player)
        if game_state.position_history.get(position_key, 0) >= 3:
            return True

        # FMJD art. 6.2: 25 moves for each player where only kings move,
        # with no man move and no capture.
        if game_state.moves_without_progress >= 50:
            return True

        # FMJD art. 6.3/6.4: reduced-material endings are counted from the
        # moment that material relation is established. Man moves and captures
        # do not reset this clock unless they change the relation itself.
        material_threshold = self._reduced_material_threshold(game_state)
        return material_threshold is not None and game_state.reduced_material_moves >= material_threshold

    def _piece_counts(self, game_state: CheckersState) -> tuple[int, int, int, int]:
        white_men = white_kings = black_men = black_kings = 0
        for slot in game_state.board.squares:
            if slot == CheckersPiece.WHITE:
                white_men += 1
            elif slot == CheckersPiece.WHITE_QUEEN:
                white_kings += 1
            elif slot == CheckersPiece.BLACK:
                black_men += 1
            elif slot == CheckersPiece.BLACK_QUEEN:
                black_kings += 1

        return white_men, white_kings, black_men, black_kings

    def _no_progress_threshold(self, game_state: CheckersState) -> int:
        return 50

    def _reduced_material_key(self, game_state: CheckersState) -> tuple[CheckersPlayer, int] | None:
        white_men, white_kings, black_men, black_kings = self._piece_counts(game_state)
        white_total, black_total = white_men + white_kings, black_men + black_kings

        # FMJD art. 6.3/6.4 apply only when one side is reduced to a single,
        # lone king; the applicable threshold depends on the other side's
        # remaining force.
        if white_total == 1 and white_kings == 1:
            lone_player = CheckersPlayer.WHITE
            stronger_kings, stronger_men = black_kings, black_men
        elif black_total == 1 and black_kings == 1:
            lone_player = CheckersPlayer.BLACK
            stronger_kings, stronger_men = white_kings, white_men
        else:
            return None

        # 5-move rule: 2 kings, or 1 king + 1 man, or 1 king vs 1 king.
        if (stronger_kings, stronger_men) in {(2, 0), (1, 1), (1, 0)}:
            return lone_player, 10

        # 16-move rule: 3 kings, 2 kings + 1 man, or 1 king + 2 men vs 1 king.
        if (stronger_kings, stronger_men) in {(3, 0), (2, 1), (1, 2)}:
            return lone_player, 32

        return None

    def _reduced_material_threshold(self, game_state: CheckersState) -> int | None:
        material_key = self._reduced_material_key(game_state)
        if material_key is None:
            return None
        return material_key[1]

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
                tl_index, tr_index = game_state.board._get_left_up(index), game_state.board._get_right_up(index)
                if tl_index is not None and game_state.board.get_piece(tl_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tl_index))
                if tr_index is not None and game_state.board.get_piece(tr_index) == CheckersPiece.EMPTY:
                    moves.append(str(index)+"-"+str(tr_index))

            elif slot == CheckersPiece.BLACK and player == CheckersPlayer.BLACK:
                tl_index, tr_index = game_state.board._get_left_down(index), game_state.board._get_right_down(index)
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
                moves += self._captures_for_square(game_state, index, str(index))

        return moves

    def _captures_for_square(
        self,
        game_state: CheckersState,
        index: int,
        move_string: str,
        captured: frozenset[int] | None = None,
    ) -> list[Move]:
        if captured is None:
            captured = frozenset()

        piece = game_state.board.get_piece(index)
        if piece in (CheckersPiece.WHITE, CheckersPiece.BLACK):
            return self._capture_sequences_for_man(game_state, index, move_string, captured)
        return self._capture_sequences_for_queen(game_state, index, move_string, captured)

    def _capture_sequences_for_man(
        self,
        game_state: CheckersState,
        index: int,
        move_string: str,
        captured: frozenset[int],
    ) -> list[Move]:
        piece = game_state.board.get_piece(index)
        capture_directions = [0, 1, 2, 3]
        sequences = []
        found_capture = False

        for direction_id in capture_directions:
            neighbour_index = game_state.board.get_closest_index(index, direction_id)
            if neighbour_index is None:
                continue
            neighbour_piece = game_state.board.get_piece(neighbour_index)
            if neighbour_index in captured:
                continue
            if neighbour_piece not in self._pieces_from_piece(piece, opposite=True):
                continue

            landing_index = game_state.board.get_closest_index(neighbour_index, direction_id)
            if landing_index is None:
                continue
            if game_state.board.get_piece(landing_index) != CheckersPiece.EMPTY:
                continue

            found_capture = True
            next_board = deepcopy(game_state.board)
            next_board.set_piece(index, CheckersPiece.EMPTY)
            next_board.set_piece(landing_index, piece)
            next_state = CheckersState(next_board, game_state.active_player)
            next_captured = captured | {neighbour_index}

            next_move = f"{move_string}x{landing_index}"

            continuations = self._capture_sequences_for_man(next_state, landing_index, next_move, next_captured)
            if continuations:
                sequences.extend(continuations)
            else:
                sequences.append(next_move)

        if not found_capture and 'x' in move_string:
            return [move_string]
        return sequences

    def _capture_sequences_for_queen(
        self,
        game_state: CheckersState,
        index: int,
        move_string: str,
        captured: frozenset[int],
    ) -> list[Move]:

        piece = game_state.board.get_piece(index)
        sequences = []
        found_capture = False

        for direction_id in range(4):
            diagonal = game_state.board._get_diagonal(index, direction_id)
            enemy_index = None
            for candidate_index in diagonal:
                candidate_piece = game_state.board.get_piece(candidate_index)
                if candidate_index in captured:
                    break
                if candidate_piece == CheckersPiece.EMPTY:
                    if enemy_index is None:
                        continue
                    next_board = deepcopy(game_state.board)
                    next_board.set_piece(index, CheckersPiece.EMPTY)
                    next_board.set_piece(candidate_index, piece)
                    next_state = CheckersState(next_board, game_state.active_player)
                    next_captured = captured | {enemy_index}
                    next_move = f"{move_string}x{candidate_index}"
                    found_capture = True
                    continuations = self._capture_sequences_for_queen(
                        next_state,
                        candidate_index,
                        next_move,
                        next_captured,
                    )
                    if continuations:
                        sequences.extend(continuations)
                    else:
                        sequences.append(next_move)
                    continue

                if candidate_piece in self._pieces_from_piece(piece, opposite=True):
                    if enemy_index is None:
                        enemy_index = candidate_index
                    else:
                        break
                else:
                    break

        if not found_capture and 'x' in move_string:
            return [move_string]
        return sequences

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
        previous_material_key = game_state.reduced_material_key
        if previous_material_key is None:
            previous_material_key = self._reduced_material_key(game_state)

        promotion_fields = list(range(0, CheckersBoard.SQUARES_PER_ROW))
        queen_piece = CheckersPiece.WHITE_QUEEN
        if game_state.get_player() == CheckersPlayer.BLACK:
            queen_piece = CheckersPiece.BLACK_QUEEN
            promotion_fields = list(range(
                CheckersBoard.PLAYABLE_SQUARES - CheckersBoard.SQUARES_PER_ROW,
                CheckersBoard.PLAYABLE_SQUARES,
            ))

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

        # Draw-rule bookkeeping: resets on ANY man move (even without
        # capture) or ANY capture (even by a king) - only a pure king
        # non-capturing move increments the counter.
        is_capture = 'x' in move
        moved_a_man = start_piece in (CheckersPiece.WHITE, CheckersPiece.BLACK)
        if is_capture or moved_a_man:
            game_state.moves_without_progress = 0
        else:
            game_state.moves_without_progress += 1

        current_material_key = self._reduced_material_key(game_state)
        if current_material_key is None or self._reduced_material_threshold(game_state) is None:
            game_state.reduced_material_key = None
            game_state.reduced_material_moves = 0
        elif current_material_key == previous_material_key:
            game_state.reduced_material_key = current_material_key
            game_state.reduced_material_moves += 1
        else:
            game_state.reduced_material_key = current_material_key
            game_state.reduced_material_moves = 0

        # Switch player
        game_state = self._switch_player(game_state)

        # Repetition tracking (position + side to move)
        position_key = (tuple(game_state.board.squares), game_state.active_player)
        game_state.position_history[position_key] = game_state.position_history.get(position_key, 0) + 1

        return game_state

    def _get_inbetween_fields(self, state: CheckersState, start_field: int, final_field: int) -> int:
        for dir_pair in [[0, 3], [3, 0], [1, 2], [2, 1]]:
            dir1, dir2 = dir_pair[0], dir_pair[1]
            diagonal = state.board._get_diagonal(start_field, dir1)
            if final_field in diagonal:
                opposite_diagonal = state.board._get_diagonal(
                    final_field, dir2)
                return [field for field in opposite_diagonal if field in diagonal]

    def _is_promotion_square(self, piece: CheckersPiece, index: int) -> bool:
        if piece == CheckersPiece.WHITE:
            return index < CheckersBoard.SQUARES_PER_ROW
        if piece == CheckersPiece.BLACK:
            return index >= CheckersBoard.PLAYABLE_SQUARES - CheckersBoard.SQUARES_PER_ROW
        return False

    def _switch_player(self, state: CheckersState):
        if state.get_player() == CheckersPlayer.WHITE:
            state.active_player = CheckersPlayer.BLACK
        else:
            state.active_player = CheckersPlayer.WHITE
        return state
