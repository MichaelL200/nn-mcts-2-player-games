from src.games.checkers import Checkers, CheckersPiece, CheckersPlayer, CheckersState, CheckersBoard


def test_is_terminal_white_wins():
    game = Checkers()
    board = CheckersBoard([
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.WHITE, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
    ])
    game_state = CheckersState(board, CheckersPlayer.WHITE)
    assert game.is_terminal(game_state) is True


def test_is_terminal_black_wins():
    game = Checkers()
    board = CheckersBoard([
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
        CheckersPiece.BLACK, CheckersPiece.EMPTY, CheckersPiece.EMPTY, CheckersPiece.EMPTY,
    ])
    game_state = CheckersState(board, CheckersPlayer.BLACK)
    assert game.is_terminal(game_state) is True


def test_is_terminal_start():
    game = Checkers()
    state = game.get_starting_state()
    assert game.is_terminal(state) is False
