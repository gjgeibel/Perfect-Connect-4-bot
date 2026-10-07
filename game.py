import time

from board import ConnectFourBoard, InvalidMoveError
from player import CPUPlayer, ConsolePlayer, MatplotlibPlayer


class MatplotlibDisplay:
    """Display the Connect Four board in a Matplotlib window."""

    def __init__(self, player_1_symbol, player_2_symbol):
        import matplotlib.pyplot as plt

        self.plt = plt
        self.player_1_symbol = player_1_symbol
        self.player_2_symbol = player_2_symbol

        self.fig, self.ax = plt.subplots()
        plt.show(block=False)

    def draw(
        self,
        board,
        message="Click a column to play.",
        xlabel="Click the column where you want to play",
    ):
        """Draw the current board state."""

        self.ax.clear()

        for row in range(board.num_rows):
            for col in range(board.num_cols):
                symbol = board.rows[row][col]

                if symbol == self.player_1_symbol:
                    color = "red"
                elif symbol == self.player_2_symbol:
                    color = "yellow"
                else:
                    color = "white"

                self.ax.scatter(
                    col,
                    row,
                    s=1200,
                    color=color,
                    edgecolors="black",
                )

        self.ax.set_xlim(
            -0.5,
            board.num_cols - 0.5,
        )

        self.ax.set_ylim(
            board.num_rows - 0.5,
            -0.5,
        )

        self.ax.set_xticks(
            range(board.num_cols)
        )

        self.ax.set_yticks(
            range(board.num_rows)
        )

        self.ax.set_title(message)
        self.ax.set_xlabel(xlabel)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def get_column(self, board, player_name):
        """Wait for a human player to click a column."""

        self.draw(
            board,
            f"{player_name}'s turn - click a column",
            "Click the column where you want to play",
        )

        click = self.plt.ginput(1)

        if not click:
            return -1

        x, _ = click[0]

        return int(round(x))


class ConnectFourGame:
    """Manage the Connect Four board and players."""

    def __init__(
        self,
        rows=6,
        cols=7,
        p1_type=ConsolePlayer,
        p2_type=ConsolePlayer,
        display_mode="console",
    ):
        """Initialize a new Connect Four game."""

        self.display_mode = display_mode
        self.board = ConnectFourBoard(
            rows,
            cols,
        )

        if (
            p1_type is CPUPlayer
            and p2_type is CPUPlayer
        ):
            p1_name = "CPU 1"
            p2_name = "CPU 2"

        elif p1_type is CPUPlayer:
            p1_name = "CPU"
            p2_name = "Player 2"

        elif p2_type is CPUPlayer:
            p1_name = "Player 1"
            p2_name = "CPU"

        else:
            p1_name = "Player 1"
            p2_name = "Player 2"

        p1_symbol = self.get_player_symbol(
            p1_name
        )

        p2_symbol = self.get_player_symbol(
            p2_name
        )

        while p2_symbol == p1_symbol:
            print(
                f"{p2_name} can't have the same "
                f"symbol as {p1_name}!"
            )

            p2_symbol = self.get_player_symbol(
                p2_name
            )

        self.player_1 = p1_type(
            name=p1_name,
            symbol=p1_symbol,
        )

        self.player_2 = p2_type(
            name=p2_name,
            symbol=p2_symbol,
        )

        self.turn = 0

        self.cpu_vs_cpu = (
            p1_type is CPUPlayer
            and p2_type is CPUPlayer
        )

        if self.display_mode == "matplotlib":
            self.display = MatplotlibDisplay(
                p1_symbol,
                p2_symbol,
            )
        else:
            self.display = None

    def show_board(
        self,
        message="",
        xlabel=None,
    ):
        """Show the board using the selected display mode."""

        if self.display_mode == "matplotlib":

            if xlabel is None:
                if self.cpu_vs_cpu:
                    xlabel = (
                        "CPU vs CPU perfect-play "
                        "demonstration"
                    )
                else:
                    xlabel = (
                        "Click the column where "
                        "you want to play"
                    )

            self.display.draw(
                self.board,
                message,
                xlabel,
            )

        else:
            self.board.display()

    def pause_after_cpu_move(self):
        """Pause briefly so CPU moves can be observed."""

        if not self.cpu_vs_cpu:
            return

        if self.display_mode == "matplotlib":
            self.display.plt.pause(0.5)
        else:
            time.sleep(0.5)

    def start(self):
        """Play until somebody wins or the board becomes full."""

        self.board.clear()
        self.turn = 0

        if self.display_mode == "matplotlib":

            if self.cpu_vs_cpu:
                self.show_board(
                    "CPU 1 vs CPU 2"
                )
            else:
                self.show_board(
                    "Connect 4"
                )

        while not self.board.is_full():

            if self.turn % 2 == 0:
                current_player = self.player_1
            else:
                current_player = self.player_2

            print(
                f"\n{current_player.name}'s turn."
            )

            if self.display_mode == "console":
                self.board.display()

            move_is_invalid = True

            while move_is_invalid:

                col = current_player.move(
                    board=self.board,
                    display=self.display,
                )

                try:
                    self.board.add_piece(
                        col,
                        current_player.symbol,
                    )

                    move_is_invalid = False

                except InvalidMoveError as err:
                    print(err)

            self.turn += 1

            if self.display_mode == "matplotlib":

                if self.cpu_vs_cpu:

                    self.show_board(
                        (
                            f"{current_player.name} "
                            f"played column {col}"
                        ),
                        (
                            "CPU vs CPU perfect-play "
                            "game"
                        ),
                    )

                else:

                    self.show_board(
                        (
                            f"{current_player.name} "
                            f"played column {col}"
                        )
                    )

            self.pause_after_cpu_move()

            if self.board.check_winner():

                print()

                if self.display_mode == "matplotlib":

                    if self.cpu_vs_cpu:

                        self.show_board(
                            (
                                f"{current_player.name} "
                                "wins!"
                            ),
                            (
                                "CPU vs CPU perfect-play "
                                "game"
                            ),
                        )

                    else:

                        self.show_board(
                            f"{current_player.name} wins!"
                        )

                else:
                    self.show_board()

                print(
                    f"{current_player.name} wins!"
                )

                break

        else:

            print()

            if self.display_mode == "matplotlib":

                if self.cpu_vs_cpu:

                    self.show_board(
                        "No winner!",
                        (
                            "CPU vs CPU perfect-play "
                            "game"
                        ),
                    )

                else:
                    self.show_board(
                        "No winner!"
                    )

            else:
                self.show_board()

            print("No winner!")

    def get_player_symbol(
        self,
        player_name,
    ):
        """Request a valid symbol for a player."""

        while True:

            symbol = input(
                "Enter a letter to use as a "
                f"symbol for {player_name}: "
            ).strip()

            if not symbol:

                print(
                    "Symbol must not be a "
                    "whitespace character!"
                )

                continue

            symbol = symbol[0]

            confirmation = input(
                f'Use "{symbol}" for '
                f"{player_name}? (y/N): "
            )

            if confirmation.lower().startswith(
                "y" or "Y"
            ):
                return symbol


def choose_game_type():
    """Ask which player configuration should be used."""

    while True:

        print()
        print("Connect 4")
        print("1. Play against the CPU")
        print("2. Play against another person")
        print("3. CPU vs CPU")

        choice = input(
            "Choose game type (1, 2, or 3): "
        ).strip()

        if choice in {
            "1",
            "2",
            "3",
        }:
            return choice

        print(
            "Please enter 1, 2, or 3."
        )


def choose_display_mode():
    """Ask which display mode should be used."""

    while True:

        print()
        print("Display Modes")
        print("1. Console display")
        print("2. Matplotlib display")

        choice = input(
            "Choose display mode (1 or 2): "
        ).strip()

        if choice == "1":
            return "console"

        if choice == "2":
            return "matplotlib"

        print(
            "Please enter 1 or 2."
        )


def get_player_types(
    game_type,
    display_mode,
):
    """Return player classes for the selected game mode."""

    if game_type == "3":
        return CPUPlayer, CPUPlayer

    if display_mode == "matplotlib":
        human_player = MatplotlibPlayer
    else:
        human_player = ConsolePlayer

    if game_type == "1":
        return (
            human_player,
            CPUPlayer,
        )

    return (
        human_player,
        human_player,
    )


if __name__ == "__main__":

    display_mode = choose_display_mode()

    game_type = choose_game_type()

    player_1_type, player_2_type = (
        get_player_types(
            game_type,
            display_mode,
        )
    )

    game = ConnectFourGame(
        p1_type=player_1_type,
        p2_type=player_2_type,
        display_mode=display_mode,
    )

    keep_playing = True

    while keep_playing:

        game.start()

        keep_playing = input(
            "Play again? (y/N): "
        ).lower().startswith("y")

    