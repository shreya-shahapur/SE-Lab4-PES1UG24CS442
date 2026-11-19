import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from board import Board
from game import Game


def tiles(board):
    return sum(1 for row in board.grid for x in row if x)


def run_game(game, inputs):
    out = io.StringIO()
    with patch("builtins.input", side_effect=inputs), redirect_stdout(out):
        game.run()
    return out.getvalue()


class TestSlideLine(unittest.TestCase):
    def test_ordinary_slide(self):
        self.assertEqual(Board.slide_line([0, 2, 0, 4]), [2, 4, 0, 0])

    def test_four_equal(self):
        self.assertEqual(Board.slide_line([2, 2, 2, 2]), [4, 4, 0, 0])

    def test_no_chain_merge(self):          # the original bug
        self.assertEqual(Board.slide_line([2, 2, 4, 0]), [4, 4, 0, 0])
        self.assertEqual(Board.slide_line([4, 4, 8, 0]), [8, 8, 0, 0])

    def test_three_equal(self):
        self.assertEqual(Board.slide_line([2, 2, 2, 0]), [4, 2, 0, 0])

    def test_separated_equal_pair(self):
        self.assertEqual(Board.slide_line([2, 0, 2, 4]), [4, 4, 0, 0])
        self.assertEqual(Board.slide_line([2, 4, 2, 4]), [2, 4, 2, 4])

    def test_score_and_merge_count(self):
        self.assertEqual(Board.merge_line([2, 2, 4, 4]), ([4, 8, 0, 0], 12, 2))


class TestMoves(unittest.TestCase):
    def setUp(self):
        self.g = Game()
        self.b = self.g.board

    def set_grid(self, grid, score=0):
        self.b.grid = [row[:] for row in grid]
        self.b.score = score

    def test_all_four_directions(self):
        base = [[2, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4]
        self.set_grid(base); self.b.move_left()
        self.assertEqual(self.b.grid[0], [4, 0, 0, 0])
        self.set_grid(base); self.b.move_right()
        self.assertEqual(self.b.grid[0], [0, 0, 0, 4])
        col = [[2, 0, 0, 0], [2, 0, 0, 0], [0] * 4, [0] * 4]
        self.set_grid(col); self.b.move_up()
        self.assertEqual([r[0] for r in self.b.grid], [4, 0, 0, 0])
        self.set_grid(col); self.b.move_down()
        self.assertEqual([r[0] for r in self.b.grid], [0, 0, 0, 4])

    def test_score_increases_on_merge(self):
        self.set_grid([[2, 2, 4, 4], [0] * 4, [0] * 4, [0] * 4])
        self.b.move_left()
        self.assertEqual(self.b.score, 12)

    def test_unchanged_move_no_tile_no_change(self):
        self.set_grid([[2, 4, 0, 0], [0] * 4, [0] * 4, [0] * 4])
        before = [r[:] for r in self.b.grid]
        r = self.g.move("a")
        self.assertEqual(r.status, "unchanged")
        self.assertEqual(self.b.grid, before)
        self.assertNotIn("Moved", r.message)

    def test_successful_move_spawns_exactly_one_tile(self):
        self.set_grid([[0, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4])
        r = self.g.move("a")
        self.assertEqual(r.status, "moved")
        self.assertEqual(tiles(self.b), 2)

    def test_best_score_tracked(self):
        self.set_grid([[2, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4])
        self.g.move("a")
        self.assertEqual(self.g.best_score, 4)

    def test_feedback_message(self):
        self.set_grid([[2, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4])
        r = self.g.move("a")
        self.assertEqual(r.message, "Moved left. Merged 1 pair (+4).")
        self.set_grid([[0, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4])
        self.assertEqual(self.g.move("a").message, "Moved left. No merges.")

    def test_invalid_move_keys(self):
        for k in ["", "wa", "x", "1"]:
            self.assertEqual(self.g.move(k).status, "invalid")


class TestUndo(unittest.TestCase):
    def setUp(self):
        self.g = Game()
        self.b = self.g.board
        self.b.grid = [[2, 2, 4, 0], [0, 0, 0, 2], [0] * 4, [0] * 4]
        self.b.score = 10

    def test_undo_restores_board_and_score_without_new_tile(self):
        before = ([r[:] for r in self.b.grid], self.b.score)
        self.assertEqual(self.g.move("a").status, "moved")
        self.assertNotEqual(self.b.score, 10)
        self.assertEqual(self.g.undo().status, "undone")
        self.assertEqual((self.b.grid, self.b.score), before)

    def test_undo_only_one_level(self):
        self.g.move("a"); self.g.undo()
        self.assertEqual(self.g.undo().message, "Nothing to undo.")

    def test_nothing_to_undo_at_start(self):
        self.assertEqual(Game().undo().status, "invalid")

    def test_unchanged_move_is_not_undoable(self):
        self.b.grid = [[2, 4, 0, 0], [0] * 4, [0] * 4, [0] * 4]
        self.g.move("a")
        self.assertEqual(self.g.undo().status, "invalid")

    def test_best_score_survives_undo(self):
        self.g.move("a")
        best = self.g.best_score
        self.g.undo()
        self.assertEqual(self.g.best_score, best)


class TestGameEnd(unittest.TestCase):
    def test_win_at_2048(self):
        g = Game()
        g.board.grid = [[2048, 0, 0, 0]] + [[0] * 4 for _ in range(3)]
        out = run_game(g, [])           # no input should be requested
        self.assertIn("You reached 2048", out)

    def test_merge_into_2048_ends_game(self):
        g = Game()
        g.board.grid = [[1024, 1024, 0, 0]] + [[0] * 4 for _ in range(3)]
        out = run_game(g, ["a"])
        self.assertIn("You reached 2048", out)

    def test_no_moves_ends_game(self):
        g = Game()
        g.board.grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        self.assertFalse(g.board.can_move())
        self.assertIn("No legal moves", run_game(g, []))

    def test_full_board_with_pair_can_move(self):
        b = Board()
        b.grid = [[2, 2, 4, 8], [4, 8, 16, 32], [8, 16, 32, 64], [16, 32, 64, 128]]
        self.assertTrue(b.can_move())


class TestRunLoop(unittest.TestCase):
    def test_quit(self):
        out = run_game(Game(), ["q"])
        self.assertIn("W/A/S/D", out)

    def test_invalid_commands_then_quit(self):
        out = run_game(Game(), ["", "wa", "x", "q"])
        self.assertEqual(out.count("Invalid command"), 3)

    def test_undo_command_in_loop(self):
        out = run_game(Game(), ["u", "q"])
        self.assertIn("Nothing to undo.", out)

    def test_uppercase_accepted(self):
        out = run_game(Game(), ["Q"])
        self.assertNotIn("Invalid", out)


if __name__ == "__main__":
    unittest.main()
