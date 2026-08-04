from src.games.checkers import Checkers, CheckersPiece, CheckersPlayer, CheckersState, CheckersBoard


EMPTY_BOARD = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES


def test_is_terminal_white_wins():
    game = Checkers()
    board = CheckersBoard(EMPTY_BOARD.copy())
    board.set_piece(48, CheckersPiece.WHITE)
    game_state = CheckersState(board, CheckersPlayer.WHITE)
    assert game.is_terminal(game_state) is True


def test_is_terminal_black_wins():
    game = Checkers()
    board = CheckersBoard(EMPTY_BOARD.copy())
    board.set_piece(48, CheckersPiece.BLACK)
    game_state = CheckersState(board, CheckersPlayer.BLACK)
    assert game.is_terminal(game_state) is True


def test_is_terminal_start():
    game = Checkers()
    state = game.get_starting_state()
    assert game.is_terminal(state) is False


def test_starting_state_uses_10x10_board():
    game = Checkers()
    state = game.get_starting_state()
    squares = state.board.get_squares().tolist()

    assert len(squares) == CheckersBoard.PLAYABLE_SQUARES
    assert state.get_player() == CheckersPlayer.WHITE
    assert squares[:20] == [CheckersPiece.BLACK] * 20
    assert squares[20:30] == [CheckersPiece.EMPTY] * 10
    assert squares[30:] == [CheckersPiece.WHITE] * 20


def test_white_man_can_capture_backward():
    game = Checkers()
    squares = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES
    squares[12] = CheckersPiece.WHITE
    squares[17] = CheckersPiece.BLACK

    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game.get_moves(state) == ['12x21']


def test_capture_stops_on_promotion_row():
    game = Checkers()
    squares = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES
    squares[12] = CheckersPiece.WHITE
    squares[7] = CheckersPiece.BLACK
    squares[6] = CheckersPiece.BLACK

    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game.get_moves(state) == ['12x1x10']

    next_state = game.make_move(state, '12x1x10')

    assert next_state.board.get_piece(10) == CheckersPiece.WHITE
    assert next_state.get_player() == CheckersPlayer.BLACK


def test_queen_has_flying_capture_options():
    game = Checkers()
    squares = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES
    squares[22] = CheckersPiece.WHITE_QUEEN
    squares[28] = CheckersPiece.BLACK

    state = CheckersState(CheckersBoard(squares), CheckersPlayer.WHITE)

    assert game.get_moves(state) == ['22x33', '22x39', '22x44']
