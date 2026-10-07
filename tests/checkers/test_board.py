from src.games.checkers import CheckersBoard, CheckersPiece


BOARD = [CheckersPiece.EMPTY] * CheckersBoard.PLAYABLE_SQUARES


def test_get_left_up_present():
    assert CheckersBoard._get_left_up(12) == 7
    assert CheckersBoard._get_left_up(13) == 8
    assert CheckersBoard._get_left_up(23) == 18


def test_get_left_up_left_edge():
    assert CheckersBoard._get_left_up(5) is None
    assert CheckersBoard._get_left_up(15) is None
    assert CheckersBoard._get_left_up(25) is None


def test_get_left_up_top_edge():
    assert CheckersBoard._get_left_up(0) is None
    assert CheckersBoard._get_left_up(1) is None
    assert CheckersBoard._get_left_up(2) is None
    assert CheckersBoard._get_left_up(3) is None
    assert CheckersBoard._get_left_up(4) is None


def test_get_right_up_present():
    assert CheckersBoard._get_right_up(12) == 8
    assert CheckersBoard._get_right_up(13) == 9
    assert CheckersBoard._get_right_up(23) == 19


def test_get_right_up_right_edge():
    assert CheckersBoard._get_right_up(4) is None
    assert CheckersBoard._get_right_up(14) is None
    assert CheckersBoard._get_right_up(24) is None
    assert CheckersBoard._get_right_up(34) is None
    assert CheckersBoard._get_right_up(44) is None


def test_get_right_up_top_edge():
    assert CheckersBoard._get_right_up(0) is None
    assert CheckersBoard._get_right_up(1) is None
    assert CheckersBoard._get_right_up(2) is None
    assert CheckersBoard._get_right_up(3) is None
    assert CheckersBoard._get_right_up(4) is None


def test_get_left_down_present():
    assert CheckersBoard._get_left_down(12) == 17
    assert CheckersBoard._get_left_down(13) == 18
    assert CheckersBoard._get_left_down(23) == 28


def test_get_left_down_left_edge():
    assert CheckersBoard._get_left_down(5) is None
    assert CheckersBoard._get_left_down(15) is None
    assert CheckersBoard._get_left_down(25) is None


def test_get_left_down_bottom_edge():
    assert CheckersBoard._get_left_down(45) is None
    assert CheckersBoard._get_left_down(46) is None
    assert CheckersBoard._get_left_down(47) is None
    assert CheckersBoard._get_left_down(48) is None
    assert CheckersBoard._get_left_down(49) is None


def test_get_right_down_present():
    assert CheckersBoard._get_right_down(12) == 18
    assert CheckersBoard._get_right_down(13) == 19
    assert CheckersBoard._get_right_down(23) == 29


def test_get_right_down_right_edge():
    assert CheckersBoard._get_right_down(4) is None
    assert CheckersBoard._get_right_down(14) is None
    assert CheckersBoard._get_right_down(24) is None
    assert CheckersBoard._get_right_down(34) is None
    assert CheckersBoard._get_right_down(44) is None


def test_get_right_down_bottom_edge():
    assert CheckersBoard._get_right_down(45) is None
    assert CheckersBoard._get_right_down(46) is None
    assert CheckersBoard._get_right_down(47) is None
    assert CheckersBoard._get_right_down(48) is None
    assert CheckersBoard._get_right_down(49) is None


def test_get_closest_indexes_middle_position():
    board = CheckersBoard(BOARD.copy())

    indexes = board.get_closest_indexes(12)
    assert indexes == [7, 8, 17, 18]

    indexes = board.get_closest_indexes(13)
    assert indexes == [8, 9, 18, 19]


def test_get_closest_indexes_edge_positions():
    board = CheckersBoard(BOARD.copy())

    top_left = board.get_closest_indexes(0)
    assert top_left == [None, None, 5, 6]

    top_right = board.get_closest_indexes(4)
    assert top_right == [None, None, 9, None]

    right_edge = board.get_closest_indexes(19)
    assert right_edge == [13, 14, 23, 24]

    bottom_left = board.get_closest_indexes(45)
    assert bottom_left == [None, 40, None, None]


def test_get_closest_occupied_indexes_with_pieces():
    squares = BOARD.copy()
    squares[7] = CheckersPiece.BLACK
    squares[8] = CheckersPiece.WHITE

    board = CheckersBoard(squares)

    occupied = board.get_closest_occupied_indexes(12)
    assert occupied == [7, 8, None, None]


def test_get_piece():
    squares = BOARD.copy()
    squares[5] = CheckersPiece.BLACK
    squares[10] = CheckersPiece.WHITE
    squares[15] = CheckersPiece.BLACK_QUEEN
    squares[20] = CheckersPiece.WHITE_QUEEN

    board = CheckersBoard(squares)

    assert board.get_piece(5) == CheckersPiece.BLACK
    assert board.get_piece(10) == CheckersPiece.WHITE
    assert board.get_piece(15) == CheckersPiece.BLACK_QUEEN
    assert board.get_piece(20) == CheckersPiece.WHITE_QUEEN
    assert board.get_piece(0) == CheckersPiece.EMPTY
