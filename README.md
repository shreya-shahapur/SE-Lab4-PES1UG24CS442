# Lab 4 — VibeCoding: 2048 (Scenario 14)

A terminal implementation of 2048 with directional movement and tile merging.
This lab fixes the broken merge logic in the starter code and adds game-state
handling, one-level undo, best score, and move feedback.

## Files

| File | Purpose |
|---|---|
| `main.py` | Entry point. |
| `game.py` | Game loop, commands, undo, best score, move feedback. |
| `board.py` | Grid movement, merge logic, scoring, win / no-move checks. |
| `test_game.py` | Unit tests (standard library `unittest`). |
| `requirements.txt` | Dependency declaration (none required). |
| `SE_lab4_before-recording.mp4` | 10-second video of the original, buggy behaviour. |
| `SE_lab4_after-recording.mp4` | 10-second video of the fixed game with the new features. |
| Chat history export | Complete LLM chat history (doc/PDF). |

## How to run

```bash
python main.py
```

Python 3.9+ is recommended. No packages need to be installed.

### Controls

| Key | Action |
|---|---|
| `W` / `A` / `S` / `D` | Move up / left / down / right |
| `U` | Undo the last successful move (one level) |
| `Q` | Quit |

Input is case-insensitive. Anything else (including empty input or multiple
characters such as `wa`) is rejected as an invalid command.

### Run the tests

```bash
python -m unittest -v
```

## What was changed

### Task 1 — Correct merge semantics (`board.py`)

**Original defect:** `slide_line` merged into the last element of the result
list, so a tile created by a merge could merge again in the same move.

| Row | Starter result (wrong) | Fixed result |
|---|---|---|
| `[2, 2, 4, 0]` | `[8, 0, 0, 0]` | `[4, 4, 0, 0]` |
| `[4, 4, 8, 0]` | `[16, 0, 0, 0]` | `[8, 8, 0, 0]` |

**Fix:** `merge_line` walks the compressed tiles left to right. When two equal
neighbours are found they are merged and **both** source tiles are skipped, so
the new tile is never compared again. Normal compression and movement are
unchanged. `slide_line` still exists and returns just the new line.

Examples of the corrected behaviour:

- `[2, 2, 2, 2]` → `[4, 4, 0, 0]`
- `[2, 2, 2, 0]` → `[4, 2, 0, 0]`
- `[2, 0, 2, 4]` → `[4, 4, 0, 0]`
- `[2, 4, 2, 4]` → unchanged

### Task 2 — Game-state handling

- **Score** now increases by the value of every merged tile (the starter never
  updated it).
- **Win detection:** reaching 2048 ends the game.
- **No-move detection:** a full board with no equal neighbours ends the game.
- **Unchanged moves** do not create a tile and do not change the board.
- **Input validation:** empty input and multi-character input are invalid.

### Task 3 — Undo and best score

- `U` restores the board **and** the score from before the last successful move.
- Undo never spawns a new tile.
- It is one level only: a second undo in a row prints `Nothing to undo.`
- Unchanged and invalid moves are not undoable.
- Best score is tracked in memory for the current run and does not drop on undo.

### Task 4 — Move feedback

One short, action-level message per command, produced in `Game.move` (not in
the board-scanning functions):

- `Moved left. Merged 1 pair (+4).`
- `Moved left. No merges.`
- `Nothing moved.` (unchanged move)
- `Invalid command. Use W/A/S/D, U to undo, Q to quit.`
- `Undid last move.` / `Nothing to undo.`

## Testing

`test_game.py` covers:

- ordinary slides and all four move directions
- four-equal patterns and three-equal patterns
- separated equal pairs
- the original double-merge defect
- unchanged moves (no tile, board untouched, no "moved" message)
- 2048 detection (including a merge that creates 2048)
- no-move boards and a full board that can still move
- undo, score restoration, double undo, undo with nothing to undo
- best score tracking
- invalid commands, uppercase input, and quitting

## Constraints respected

- Standard library only; no external dependencies added.
- All state is kept in memory; no CSV, JSON, SQLite or other persistence.
- The original project structure is kept and the code stays modular.

## Submission checklist

- [x] Task 1 completed; original defect reproduced and fixed
- [x] Tasks 2–4 completed and tested
- [x] Boundary and invalid-input cases tested
- [x] No unnecessary external dependencies added
- [x] No persistent storage added
- [x] Code remains understandable and modular
- [ ] Complete LLM chat-history link included: `<paste chat link here>`
