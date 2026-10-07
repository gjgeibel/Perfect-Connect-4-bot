from abc import ABC, abstractmethod
from solver import PerfectSolver, position_from_board


class AbstractPlayer(ABC):
    def __init__(self, symbol, name):
        self.name = name
        self.symbol = symbol

    @abstractmethod
    def move(self, **kwargs):
        """Return the column where the player intends to play a piece."""


class ConsolePlayer(AbstractPlayer):
    def move(self, **kwargs):
        while True:
            try:
                return int(input('Enter which column to play in: '))
            except ValueError:
                print('Please enter a column number.')


class MatplotlibPlayer(AbstractPlayer):
    def move(self, **kwargs):
        board = kwargs['board']
        display = kwargs['display']
        return display.get_column(board, self.name)


class CPUPlayer(AbstractPlayer):
    _solver = None

    def move(self, **kwargs):
        board = kwargs['board']
        if board.num_rows != 6 or board.num_cols != 7:
            raise ValueError('Perfect CPU requires the standard 7x6 board.')
        if CPUPlayer._solver is None:
            CPUPlayer._solver = PerfectSolver()
        if CPUPlayer._solver.book.depth < 0:
            raise RuntimeError(
                'Missing 7x6.book. Put Pascal Pons\' 7x6.book in the same '
                'folder as game.py. See README.txt for the one-time setup.'
            )
        position = position_from_board(board, self.symbol)
        col = CPUPlayer._solver.best_move(position)
        print(f'CPU chooses column {col}.')
        return col
