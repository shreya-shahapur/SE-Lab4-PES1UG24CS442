import copy
import random

SIZE = 4
WIN_TILE = 2048


class Board:
    def __init__(self):
        self.grid = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.last_gain = 0    # points scored by the most recent move
        self.last_merges = 0  # merges made by the most recent move
        self.add_random_tile()
        self.add_random_tile()

    # ---------- tile creation ----------
    def add_random_tile(self):
        empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 4 if random.random() < 0.1 else 2

    # ---------- line logic ----------
    @staticmethod
    def merge_line(line):
        """Slide a line toward index 0 and merge equal neighbours.

        Each original tile takes part in at most one merge, because after a
        pair is merged we skip BOTH source tiles and never compare the new
        tile again. Returns (new_line, points_gained, merge_count).
        """
        values = [x for x in line if x]
        result = []
        gained = 0
        merges = 0
        i = 0
        while i < len(values):
            if i + 1 < len(values) and values[i] == values[i + 1]:
                merged = values[i] * 2
                result.append(merged)
                gained += merged
                merges += 1
                i += 2
            else:
                result.append(values[i])
                i += 1
        return result + [0] * (SIZE - len(result)), gained, merges

    @staticmethod
    def slide_line(line):
        """Same behaviour as before: returns only the new line."""
        return Board.merge_line(line)[0]

    def _apply(self, lines, reverse):
        """Run merge_line on every line; update score and last-move stats."""
        new_lines = []
        changed = False
        gain = 0
        merges = 0
        for old in lines:
            src = old[::-1] if reverse else old
            new, g, m = self.merge_line(src)
            if reverse:
                new = new[::-1]
            changed |= new != old
            gain += g
            merges += m
            new_lines.append(new)
        self.score += gain
        self.last_gain = gain
        self.last_merges = merges
        return new_lines, changed

    def _columns(self):
        return [[self.grid[r][c] for r in range(SIZE)] for c in range(SIZE)]

    def _set_columns(self, cols):
        self.grid = [[cols[c][r] for c in range(SIZE)] for r in range(SIZE)]

    # ---------- moves (return True if the board changed) ----------
    def move_left(self):
        self.grid, changed = self._apply([row[:] for row in self.grid], False)
        return changed

    def move_right(self):
        self.grid, changed = self._apply([row[:] for row in self.grid], True)
        return changed

    def move_up(self):
        cols, changed = self._apply(self._columns(), False)
        self._set_columns(cols)
        return changed

    def move_down(self):
        cols, changed = self._apply(self._columns(), True)
        self._set_columns(cols)
        return changed

    # ---------- state checks ----------
    def can_move(self):
        if any(0 in row for row in self.grid):
            return True
        for r in range(SIZE):
            for c in range(SIZE):
                if c + 1 < SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r + 1 < SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def has_won(self):
        return any(x >= WIN_TILE for row in self.grid for x in row)

    # ---------- undo support ----------
    def snapshot(self):
        return copy.deepcopy(self.grid), self.score

    def restore(self, snap):
        grid, score = snap
        self.grid = copy.deepcopy(grid)
        self.score = score
        self.last_gain = 0
        self.last_merges = 0
