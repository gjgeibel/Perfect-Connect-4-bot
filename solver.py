"""Exact 7x6 Connect Four solver, adapted from Pascal Pons' algorithm.

Uses bitboards, negamax with alpha-beta pruning, a transposition table,
non-losing-move pruning, center-oriented move ordering, and the optional
7x6 opening book. The opening book is strongly recommended for fast
responses in early-game positions.
"""

from array import array
from pathlib import Path


WIDTH, HEIGHT = 7, 6
SIZE = WIDTH * HEIGHT

MIN_SCORE = -(SIZE // 2) + 3
MAX_SCORE = (SIZE + 1) // 2 - 3

BOTTOM_MASK = sum(
    1 << (col * (HEIGHT + 1))
    for col in range(WIDTH)
)

BOARD_MASK = BOTTOM_MASK * ((1 << HEIGHT) - 1)

COLUMN_MASKS = [
    ((1 << HEIGHT) - 1) << (col * (HEIGHT + 1))
    for col in range(WIDTH)
]

TOP_MASKS = [
    1 << (HEIGHT - 1 + col * (HEIGHT + 1))
    for col in range(WIDTH)
]

BOTTOM_COL = [
    1 << (col * (HEIGHT + 1))
    for col in range(WIDTH)
]

COLUMN_ORDER = [3, 4, 2, 5, 1, 6, 0]


def _winning_position(position, mask):
    r = (position << 1) & (position << 2) & (position << 3)

    p = (position << 7) & (position << 14)
    r |= p & (position << 21)
    r |= p & (position >> 7)

    p = (position >> 7) & (position >> 14)
    r |= p & (position << 7)
    r |= p & (position >> 21)

    p = (position << 6) & (position << 12)
    r |= p & (position << 18)
    r |= p & (position >> 6)

    p = (position >> 6) & (position >> 12)
    r |= p & (position << 6)
    r |= p & (position >> 18)

    p = (position << 8) & (position << 16)
    r |= p & (position << 24)
    r |= p & (position >> 8)

    p = (position >> 8) & (position >> 16)
    r |= p & (position << 8)
    r |= p & (position >> 24)

    return r & (BOARD_MASK ^ mask)


class Position:
    def __init__(self, current=0, mask=0, moves=0):
        self.current = current
        self.mask = mask
        self.moves = moves

    def copy(self):
        return Position(
            self.current,
            self.mask,
            self.moves,
        )

    def possible(self):
        return (self.mask + BOTTOM_MASK) & BOARD_MASK

    def can_play(self, col):
        return not (self.mask & TOP_MASKS[col])

    def is_winning_move(self, col):
        winning_positions = _winning_position(
            self.current,
            self.mask,
        )

        return bool(
            winning_positions
            & self.possible()
            & COLUMN_MASKS[col]
        )

    def can_win_next(self):
        winning_positions = _winning_position(
            self.current,
            self.mask,
        )

        return bool(
            winning_positions
            & self.possible()
        )

    def play_col(self, col):
        move = (
            (self.mask + BOTTOM_COL[col])
            & COLUMN_MASKS[col]
        )

        self.current ^= self.mask
        self.mask |= move
        self.moves += 1

    def key(self):
        return self.current + self.mask

    def key3(self):
        def partial(key, col):
            pos = 1 << (col * 7)

            while pos & self.mask:
                key *= 3
                key += 1 if pos & self.current else 2
                pos <<= 1

            return key * 3

        forward = 0

        for col in range(7):
            forward = partial(forward, col)

        reverse = 0

        for col in range(6, -1, -1):
            reverse = partial(reverse, col)

        return min(forward, reverse) // 3

    def possible_non_losing(self):
        possible = self.possible()

        opponent_win = _winning_position(
            self.current ^ self.mask,
            self.mask,
        )

        forced = possible & opponent_win

        if forced:
            if forced & (forced - 1):
                return 0

            possible = forced

        return possible & ~(opponent_win >> 1)

    def move_score(self, move):
        return _winning_position(
            self.current | move,
            self.mask,
        ).bit_count()


class OpeningBook:
    def __init__(self, filename):
        self.depth = -1
        self.keys = None
        self.values = None

        path = Path(filename)

        if not path.exists():
            return

        with path.open("rb") as book_file:
            header = book_file.read(6)

            if len(header) != 6:
                return

            (
                width,
                height,
                depth,
                key_bytes,
                value_bytes,
                log_size,
            ) = header

            if (width, height, value_bytes) != (7, 6, 1):
                return

            size = _next_prime(1 << log_size)

            raw_keys = book_file.read(
                size * key_bytes
            )

            raw_values = book_file.read(size)

            if (
                len(raw_keys) != size * key_bytes
                or len(raw_values) != size
            ):
                return

        code = {
            1: "B",
            2: "H",
            4: "I",
            8: "Q",
        }.get(key_bytes)

        if code is None:
            return

        keys = array(code)
        keys.frombytes(raw_keys)

        self.depth = depth
        self.size = size
        self.key_bytes = key_bytes
        self.keys = keys
        self.values = raw_values

    def get(self, position):
        if (
            self.keys is None
            or position.moves > self.depth
        ):
            return 0

        key = position.key3()
        index = key % self.size

        mask = (
            1 << (8 * self.key_bytes)
        ) - 1

        if self.keys[index] == (key & mask):
            return self.values[index]

        return 0


def _next_prime(number):
    def prime(value):
        if value < 2:
            return False

        if value % 2 == 0:
            return value == 2

        divisor = 3

        while divisor * divisor <= value:
            if value % divisor == 0:
                return False

            divisor += 2

        return True

    while not prime(number):
        number += 1

    return number


class PerfectSolver:
    def __init__(self, book_path=None):
        if book_path is None:
            book_path = Path(__file__).with_name(
                "7x6.book"
            )

        self.book = OpeningBook(book_path)
        self.table = {}

    def _negamax(self, position, alpha, beta):
        possible = position.possible_non_losing()

        if not possible:
            return -(SIZE - position.moves) // 2

        if position.moves >= SIZE - 2:
            return 0

        low = -(SIZE - 2 - position.moves) // 2

        if alpha < low:
            alpha = low

            if alpha >= beta:
                return alpha

        high = (
            SIZE - 1 - position.moves
        ) // 2

        if beta > high:
            beta = high

            if alpha >= beta:
                return beta

        key = position.key()
        entry = self.table.get(key)

        if entry:
            kind, value = entry

            if kind == "lower":
                alpha = max(alpha, value)

                if alpha >= beta:
                    return alpha

            else:
                beta = min(beta, value)

                if alpha >= beta:
                    return beta

        book_value = self.book.get(position)

        if book_value:
            return (
                book_value
                + MIN_SCORE
                - 1
            )

        moves = []

        for col in COLUMN_ORDER:
            move = possible & COLUMN_MASKS[col]

            if move:
                score = position.move_score(move)
                moves.append((score, move))

        moves.sort(reverse=True)

        for _, move in moves:
            next_position = position.copy()

            next_position.current ^= (
                next_position.mask
            )

            next_position.mask |= move
            next_position.moves += 1

            score = -self._negamax(
                next_position,
                -beta,
                -alpha,
            )

            if score >= beta:
                self.table[key] = (
                    "lower",
                    score,
                )

                return score

            alpha = max(alpha, score)

        self.table[key] = (
            "upper",
            alpha,
        )

        return alpha

    def solve(self, position, weak=True):
        if position.can_win_next():
            return (
                SIZE + 1 - position.moves
            ) // 2

        if weak:
            low = -1
            high = 1
        else:
            low = -(
                SIZE - position.moves
            ) // 2

            high = (
                SIZE + 1 - position.moves
            ) // 2

        while low < high:
            middle = low + (high - low) // 2

            if (
                middle <= 0
                and low // 2 < middle
            ):
                middle = low // 2

            elif (
                middle >= 0
                and high // 2 > middle
            ):
                middle = high // 2

            result = self._negamax(
                position,
                middle,
                middle + 1,
            )

            if result <= middle:
                high = result
            else:
                low = result

        return low

    def best_move(self, position):
        """Return the best available column for the current position."""

        # Immediate winning moves always have priority.
        for col in COLUMN_ORDER:
            if (
                position.can_play(col)
                and position.is_winning_move(col)
            ):
                return col

        best_col = None
        best_score = -999

        for col in COLUMN_ORDER:
            if not position.can_play(col):
                continue

            next_position = position.copy()
            next_position.play_col(col)

            score = -self.solve(
                next_position,
                weak=True,
            )

            if score > best_score:
                best_col = col
                best_score = score

                if score > 0:
                    break

        return best_col


def position_from_board(board, cpu_symbol):
    """Convert a 2-D board into a Position for the side to move."""

    mask = 0
    current = 0
    moves = 0

    for col in range(7):
        for bit_row in range(6):
            row = 5 - bit_row
            symbol = board.rows[row][col]

            if symbol == " ":
                continue

            bit = 1 << (
                col * 7 + bit_row
            )

            mask |= bit
            moves += 1

            if symbol == cpu_symbol:
                current |= bit

    return Position(
        current,
        mask,
        moves,
    )