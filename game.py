from collections import namedtuple

from board import Board

# status is one of: "moved", "unchanged", "invalid", "undone"
Result = namedtuple("Result", ["status", "message"])

MOVES = {"a": ("left", "move_left"), "d": ("right", "move_right"),
         "w": ("up", "move_up"), "s": ("down", "move_down")}


class Game:
    def __init__(self):
        self.board = Board()
        self.best_score = 0
        self.undo_state = None  # one-level undo: (grid, score) before last move

    def display(self):
        print("\n" + "+------+------+------+------+")
        for row in self.board.grid:
            print("|" + "|".join(f"{x:^6}" if x else f"{' ':^6}" for x in row) + "|")
            print("+------+------+------+------+")
        print("Score:", self.board.score, " Best:", self.best_score)

    def move(self, key):
        """Try one move. Returns a Result describing what actually happened."""
        if key not in MOVES:
            return Result("invalid", "Invalid command. Use W/A/S/D, U to undo, Q to quit.")
        name, method = MOVES[key]
        snap = self.board.snapshot()
        if not getattr(self.board, method)():
            return Result("unchanged", "Nothing moved.")
        self.undo_state = snap              # only successful moves are undoable
        self.board.add_random_tile()        # only successful moves spawn a tile
        self.best_score = max(self.best_score, self.board.score)
        if self.board.last_merges:
            n = self.board.last_merges
            msg = (f"Moved {name}. Merged {n} pair{'s' if n != 1 else ''} "
                   f"(+{self.board.last_gain}).")
        else:
            msg = f"Moved {name}. No merges."
        return Result("moved", msg)

    def undo(self):
        if self.undo_state is None:
            return Result("invalid", "Nothing to undo.")
        self.board.restore(self.undo_state)  # restores grid AND score, no new tile
        self.undo_state = None
        return Result("undone", "Undid last move.")

    def run(self):
        print("2048 — W/A/S/D to move, U to undo, Q to quit.")
        while True:
            self.display()
            if self.board.has_won():
                print("You reached 2048! You win.")
                return
            if not self.board.can_move():
                print("No legal moves remain. Game over.")
                return
            try:
                key = input("> ").strip().lower()
            except EOFError:
                return
            if key == "q":
                return
            result = self.undo() if key == "u" else self.move(key)
            print(result.message)
