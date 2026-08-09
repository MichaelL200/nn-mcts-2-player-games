from src.games.checkers import CheckersBoard, CheckersPiece


def test_get_left_up_present():
    assert CheckersBoard._get_left_up(8) == 4


def test_get_left_up_left_edge():
    assert CheckersBoard._get_left_up(4) is None
    assert CheckersBoard._get_left_up(12) is None
    assert CheckersBoard._get_left_up(20) is None


def test_get_left_up_top_edge():
    assert CheckersBoard._get_left_up(0) is None
    assert CheckersBoard._get_left_up(1) is None
    assert CheckersBoard._get_left_up(2) is None
    assert CheckersBoard._get_left_up(3) is None


def test_get_right_up_present():
    assert CheckersBoard._get_right_up(9) == 6


def test_get_right_up_right_edge():
    assert CheckersBoard._get_right_up(3) is None
    assert CheckersBoard._get_right_up(11) is None
    assert CheckersBoard._get_right_up(19) is None
    assert CheckersBoard._get_right_up(27) is None


def test_get_right_up_top_edge():
    assert CheckersBoard._get_right_up(0) is None
    assert CheckersBoard._get_right_up(1) is None
    assert CheckersBoard._get_right_up(2) is None
    assert CheckersBoard._get_right_up(3) is None


def test_get_left_down_present():
    assert CheckersBoard._get_left_down(5) == 8


def test_get_left_down_left_edge():
    assert CheckersBoard._get_left_down(4) is None
    assert CheckersBoard._get_left_down(12) is None
    assert CheckersBoard._get_left_down(20) is None


def test_get_left_down_bottom_edge():
    assert CheckersBoard._get_left_down(28) is None
    assert CheckersBoard._get_left_down(29) is None
    assert CheckersBoard._get_left_down(30) is None
    assert CheckersBoard._get_left_down(31) is None


def test_get_right_down_present():
    assert CheckersBoard._get_right_down(4) == 8


def test_get_right_down_right_edge():
    assert CheckersBoard._get_right_down(3) is None


def test_get_right_down_bottom_edge():
    assert CheckersBoard._get_right_down(28) is None
    assert CheckersBoard._get_right_down(29) is None
    assert CheckersBoard._get_right_down(30) is None
    assert CheckersBoard._get_right_down(31) is None


def test_get_closest_index():
    board = CheckersBoard([CheckersPiece.EMPTY] * 32)

    assert board.get_closest_index(8, 0) == 4
    assert board.get_closest_index(0, 0) is None

    assert board.get_closest_index(9, 1) == 6
    assert board.get_closest_index(3, 1) is None

    assert board.get_closest_index(5, 2) == 8
    assert board.get_closest_index(28, 2) is None

    assert board.get_closest_index(4, 3) == board._get_right_down(4)


def test_get_closest_indexes_normal_position():
    board = CheckersBoard([CheckersPiece.EMPTY] * 32)

    indexes = board.get_closest_indexes(13)
    assert indexes[0] == 8
    assert indexes[1] == 9
    assert indexes[2] == 16
    assert indexes[3] == 17


def test_get_closest_indexes_edge_positions():
    board = CheckersBoard([CheckersPiece.EMPTY] * 32)

    left_edge = board.get_closest_indexes(12)
    assert left_edge[0] is None
    assert left_edge[1] == 8
    assert left_edge[2] is None
    assert left_edge[3] == 16

    right_edge = board.get_closest_indexes(11)
    assert right_edge[0] == 7
    assert right_edge[1] is None
    assert right_edge[2] == 15
    assert right_edge[3] is None

    top_edge = board.get_closest_indexes(2)
    assert top_edge[0] is None
    assert top_edge[1] is None
    assert top_edge[2] == 6
    assert top_edge[3] == 7

    bottom_edge = board.get_closest_indexes(29)
    assert bottom_edge[0] == 24
    assert bottom_edge[1] == 25
    assert bottom_edge[2] is None
    assert bottom_edge[3] is None


def test_get_closest_indexes_corner_positions():
    board = CheckersBoard([CheckersPiece.EMPTY] * 32)

    top_right = board.get_closest_indexes(3)
    assert top_right[0] is None
    assert top_right[1] is None
    assert top_right[2] == 7
    assert top_right[3] is None

    bottom_left = board.get_closest_indexes(28)
    assert bottom_left[0] is None
    assert bottom_left[1] == 24
    assert bottom_left[2] is None
    assert bottom_left[3] is None


def test_get_closest_occupied_indexes_empty_board():
    board = CheckersBoard([CheckersPiece.EMPTY] * 32)

    occupied = board.get_closest_occupied_indexes(13)
    assert occupied == [None, None, None, None]


def test_get_closest_occupied_indexes_with_pieces():
    squares = [CheckersPiece.EMPTY] * 32
    squares[0] = CheckersPiece.BLACK
    squares[2] = CheckersPiece.WHITE

    board = CheckersBoard(squares)

    occupied = board.get_closest_occupied_indexes(9)
    assert occupied[0] == 0
    assert occupied[1] == 2
    assert occupied[2] is None
    assert occupied[3] is None


def test_get_closest_occupied_indexes_with_multiple_pieces():
    squares = [CheckersPiece.EMPTY] * 32
    squares[0] = CheckersPiece.BLACK
    squares[5] = CheckersPiece.WHITE

    board = CheckersBoard(squares)

    occupied = board.get_closest_occupied_indexes(14)
    assert occupied[0] == 5
    assert occupied[1] is None
    assert occupied[2] is None
    assert occupied[3] is None


def test_get_piece():
    squares = [CheckersPiece.EMPTY] * 32
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
