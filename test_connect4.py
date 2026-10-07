from pathlib import Path

import pytest

from board import ConnectFourBoard
from player import CPUPlayer
from solver import PerfectSolver, position_from_board


def test_standard_board_size():
    """Objective: The perfect bot must work on a standard 7x6 board."""
    board = ConnectFourBoard(6, 7)

    assert board.num_rows == 6
    assert board.num_cols == 7


def test_opening_book_loads():
    """The offline perfect solver must successfully load 7x6.book."""
    book_path = Path(__file__).with_name("7x6.book")

    assert book_path.exists(), "7x6.book is missing from the project folder."

    solver = PerfectSolver(book_path)

    assert solver.book.depth >= 0


def test_cpu_rejects_nonstandard_board():
    """Perfect CPU should only operate on the standard 7x6 board."""
    board = ConnectFourBoard(5, 7)
    cpu = CPUPlayer(symbol="X", name="CPU")

    with pytest.raises(ValueError):
        cpu.move(board=board)


def test_cpu_chooses_winning_move():
    """Objective: CPU should choose an immediate winning move."""
    board = ConnectFourBoard(6, 7)

    # Give CPU three pieces along the bottom row.
    board.add_piece(0, "X")
    board.add_piece(1, "X")
    board.add_piece(2, "X")

    solver = PerfectSolver()
    position = position_from_board(board, "X")

    move = solver.best_move(position)

    # Column 3 completes X X X X
    assert move == 3


def test_cpu_first_move_is_center():
    """Objective: Perfect CPU should make an optimal opening move."""
    board = ConnectFourBoard(6, 7)

    solver = PerfectSolver()
    position = position_from_board(board, "X")

    move = solver.best_move(position)

    assert move == 3


def test_first_cpu_wins_against_second_cpu():
    """
    Objective:
    When two perfect bots play, the bot moving first should win.
    """
    board = ConnectFourBoard(6, 7)
    solver = PerfectSolver()

    symbols = ["X", "O"]
    winner = None

    for turn in range(42):
        current_symbol = symbols[turn % 2]

        position = position_from_board(
            board,
            current_symbol,
        )

        column = solver.best_move(position)

        assert column is not None

        board.add_piece(column, current_symbol)

        if board.check_winner():
            winner = current_symbol
            break

    assert winner == "X"