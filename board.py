_EMPTY = ' '  # Used to indicate empty spaces in the board


class InvalidMoveError(ValueError):
    pass


class ConnectFourBoard:
    """Represents a Connect 4 board and manages its state."""

    def __init__(self, num_rows, num_cols):
        """Initialize a new board."""
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.clear()

    def clear(self):
        """Replace all pieces with empty spaces."""
        self.rows = []

        for _ in range(self.num_rows):
            self.rows.append(
                [_EMPTY for _ in range(self.num_cols)]
            )

    def display(self):
        """Display the current board state."""
        for row in range(self.num_rows):
            print(f'\t|{"|".join(self.rows[row])}|')

        print(
            '\t '
            + ' '.join(
                str(col) for col in range(self.num_cols)
            )
        )

    def check_winner(self):
        """Return True if the board contains four matching pieces in a row."""

        directions = [
            (0, 1),   # Horizontal
            (1, 0),   # Vertical
            (1, 1),   # Diagonal down-right
            (1, -1),  # Diagonal down-left
        ]

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                symbol = self.rows[row][col]

                if symbol == _EMPTY:
                    continue

                for row_change, col_change in directions:
                    matches = True

                    for step in range(1, 4):
                        check_row = row + row_change * step
                        check_col = col + col_change * step

                        if not (
                            0 <= check_row < self.num_rows
                            and 0 <= check_col < self.num_cols
                            and self.rows[check_row][check_col] == symbol
                        ):
                            matches = False
                            break

                    if matches:
                        return True

        return False

    def is_full(self):
        """Return True if there are no empty spaces left on the board."""

        for row in self.rows:
            if _EMPTY in row:
                return False

        return True

    def add_piece(self, col, symbol):
        """Add a piece to a valid column."""

        if col < 0 or col >= self.num_cols:
            raise InvalidMoveError(
                f'Column must be between 0 and {self.num_cols - 1}.'
            )

        if self.rows[0][col] != _EMPTY:
            raise InvalidMoveError('That column is full.')

        for row in reversed(range(self.num_rows)):
            if self.rows[row][col] == _EMPTY:
                self.rows[row][col] = symbol
                return