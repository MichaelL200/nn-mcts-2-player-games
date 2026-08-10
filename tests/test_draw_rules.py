from src.games.checkers import Checkers, CheckersPiece, CheckersPlayer, CheckersState, CheckersBoard


EMPTY_BOARD = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES


def test_starting_state_registers_position_history():

    game = Checkers()
    state = game.get_starting_state()

    position_key = (tuple(state.board.squares), state.active_player)
    assert state.position_history[position_key] == 1


def test_progress_resets_on_man_move():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[12] = CheckersPiece.WHITE
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=7)

    next_state = game.make_move(state, '12-8')

    assert next_state.moves_without_progress == 0


def test_progress_resets_on_capture():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[22] = CheckersPiece.WHITE_QUEEN
    squares[28] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=9)

    next_state = game.make_move(state, '22x33')

    assert next_state.moves_without_progress == 0


def test_progress_increments_on_king_move_without_capture():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=3)

    next_state = game.make_move(state, '0-5')

    assert next_state.moves_without_progress == 4


def test_is_terminal_draw_at_no_progress_threshold():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[5] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    squares[44] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=50)

    assert game.is_terminal(state) is True


def test_is_terminal_not_draw_below_no_progress_threshold():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[5] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    squares[44] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=49)

    assert game.is_terminal(state) is False


def test_reduced_material_threshold_king_vs_king():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) == 10


def test_reduced_material_threshold_three_kings_vs_one():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[1] = CheckersPiece.WHITE_QUEEN
    squares[2] = CheckersPiece.WHITE_QUEEN
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) == 32


def test_no_progress_threshold_default_with_men_on_board():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[5] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    squares[44] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._no_progress_threshold(state) == 50
    assert game._reduced_material_threshold(state) is None


def test_reduced_material_threshold_two_men_vs_one_king_is_not_five_move_rule():
    # 2 men (no king) vs 1 lone king is NOT one of the FMJD-listed 5-move
    # endgames (2 kings / 1 king+1 man / 1 king vs 1 king) - must fall
    # back to the general 25-move rule.

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[45] = CheckersPiece.BLACK
    squares[46] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) is None


def test_reduced_material_threshold_three_men_vs_one_king_is_not_sixteen_move_rule():
    # 3 men (no king) vs 1 lone king is NOT one of the FMJD-listed 16-move
    # endgames (3 kings / 2 kings+1 man / 1 king+2 men vs 1 king).

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[45] = CheckersPiece.BLACK
    squares[46] = CheckersPiece.BLACK
    squares[47] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) is None


def test_reduced_material_threshold_king_plus_man_vs_one_king():
    # 1 king + 1 man vs 1 king IS a listed 5-move endgame.

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[5] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) == 10


def test_reduced_material_threshold_large_material_advantage_falls_back_to_default():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[1] = CheckersPiece.WHITE_QUEEN
    squares[2] = CheckersPiece.WHITE_QUEEN
    squares[3] = CheckersPiece.WHITE_QUEEN
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) is None


def test_reduced_material_threshold_lone_man_is_not_special_endgame():
    # A single MAN (not yet promoted) on one side must not trigger the
    # reduced thresholds meant for a lone king.

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[45] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game._reduced_material_threshold(state) is None


def test_reduced_material_clock_counts_man_moves():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[30] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(
        CheckersBoard(squares),
        CheckersPlayer.WHITE,
        moves_without_progress=9,
        reduced_material_moves=9,
    )

    next_state = game.make_move(state, '30-25')

    assert next_state.moves_without_progress == 0
    assert next_state.reduced_material_moves == 10
    assert game.is_terminal(next_state) is True


def test_reduced_material_clock_resets_when_material_category_changes():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[1] = CheckersPiece.WHITE_QUEEN
    squares[43] = CheckersPiece.WHITE_QUEEN
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(
        CheckersBoard(squares),
        CheckersPlayer.BLACK,
        reduced_material_moves=31,
    )

    next_state = game.make_move(state, '49x38')

    assert next_state.reduced_material_moves == 0
    assert game._reduced_material_threshold(next_state) == 10
    assert game.is_terminal(next_state) is False


def test_is_terminal_draw_by_threefold_repetition():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[49] = CheckersPiece.BLACK_QUEEN
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    shuttle = ['0-5', '49-44', '5-0', '44-49'] * 2 + ['0-5']
    for move in shuttle:
        assert not game.is_terminal(state)
        state = game.make_move(state, move)

    assert game.is_terminal(state) is True


def test_reward_is_zero_on_no_progress_draw():

    game = Checkers()
    squares = EMPTY_BOARD.copy()
    squares[0] = CheckersPiece.WHITE_QUEEN
    squares[5] = CheckersPiece.WHITE
    squares[49] = CheckersPiece.BLACK_QUEEN
    squares[44] = CheckersPiece.BLACK
    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE, moves_without_progress=50)

    assert game.reward(state, CheckersPlayer.WHITE) == 0
