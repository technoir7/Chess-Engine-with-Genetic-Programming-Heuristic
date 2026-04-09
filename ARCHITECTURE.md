# Architecture Reference

This document describes the full data pipeline from internal Python board state
through JSON serialization to frontend rendering. It is intended as context for
AI coding sessions working on this codebase.

---

## 1. Internal Board Representation (Python)

### The 120-character string

The board is stored as a 120-character string on the `Position` namedtuple
(defined in `chess_logic_by_thomasahle.py`).  The layout is a **10-column ×
12-row** grid; only the inner 8×8 region is the actual chess board.  The
padding rows/columns let the move generator detect out-of-bounds moves cheaply
(any index that lands in a padding cell contains a space `' '`).

```
Index ranges (each row is 10 characters wide, including the trailing '\n'):

  0 -  9   '         \n'   (padding)
 10 - 19   '         \n'   (padding)
 20 - 29   ' rnbqkbnr\n'   rank 8  (black back rank)
 30 - 39   ' pppppppp\n'   rank 7  (black pawns)
 40 - 49   ' ........\n'   rank 6  (empty)
 50 - 59   ' ........\n'   rank 5
 60 - 69   ' ........\n'   rank 4
 70 - 79   ' ........\n'   rank 3
 80 - 89   ' PPPPPPPP\n'   rank 2  (white pawns)
 90 - 99   ' RNBQKBNR\n'   rank 1  (white back rank)
100 -109   '         \n'   (padding)
110 -119   '         \n'   (padding)
```

Named anchor constants (from the engine):

```python
A1, H1, A8, H8 = 91, 98, 21, 28
```

### Piece encoding

| Character | Meaning |
|-----------|---------|
| Uppercase `R N B Q K P` | White piece (or "current mover's" piece after rotation) |
| Lowercase `r n b q k p` | Black piece (or opponent's piece) |
| `'.'` | Empty square (inside the 8×8 board) |
| `' '` | Padding / out-of-bounds |
| `'\n'` | Row terminator (part of the padding) |

### `Position` namedtuple fields

```python
Position(board, score, wc, bc, ep, kp)
#  board  str   120-char board string
#  score  int   incremental material+PST evaluation from white's perspective
#  wc     (bool, bool)  white castling rights: (queen-side, king-side)
#  bc     (bool, bool)  black castling rights: (queen-side, king-side)
#  ep     int   en-passant target square index (0 = none)
#  kp     int   king-passant square index used for castling (0 = none)
```

### Critical rotation behaviour

`Position.move(move)` **always rotates the board** before returning:

```python
# chess_logic_by_thomasahle.py line 226
return Position(board, score, wc, bc, ep, kp).rotate()
```

`rotate()` is defined as:

```python
def rotate(self):
    return Position(
        self.board[::-1].swapcase(), -self.score,
        self.bc, self.wc,
        119 - self.ep if self.ep else 0,
        119 - self.kp if self.kp else 0)
```

Effect: the board string is **reversed** and **cases are swapped**.  After one
rotation the board is from the opponent's perspective; after two rotations it
is back to the original orientation.

**This is the most important invariant for the Flask layer:**

| State | Orientation |
|-------|-------------|
| `initial` position | White's perspective — uppercase = white |
| After white's `move()` | Black's perspective — uppercase = black |
| After AI's `move()` (second rotation) | White's perspective again |

When a position is in black's perspective, index `i` in the board string
corresponds to physical square `119 - i` in standard notation.  All
coordinate-to-square conversions must account for this.

---

## 2. Coordinate System

### Mapping: internal index ↔ algebraic square name

Two functions in `app.py` perform this conversion:

```python
def square_to_coord(square):
    # e.g. 'e4' → 65
    file_idx = ord(square[0]) - ord('a')   # 'a'=0 … 'h'=7
    rank_idx = 8 - int(square[1])          # rank 8→0, rank 1→7
    return 21 + file_idx + (rank_idx * 10)

def coord_to_square(coord):
    # e.g. 65 → 'e4'
    file_idx = (coord - 21) % 10           # 0–7
    rank_idx = (coord - 21) // 10          # 0–7
    file_char = chr(ord('a') + file_idx)
    rank_char = str(8 - rank_idx)
    return file_char + rank_char
```

These match the engine's own `parse`/`render` helpers:

```python
# chess_logic_by_thomasahle.py
def parse(c):   return A1 + (ord(c[0])-ord('a')) - 10*(int(c[1])-1)
def render(i):  rank, fil = divmod(i-A1, 10); return chr(fil+ord('a'))+str(-rank+1)
```

### Quick reference table

| Square | Index |   | Square | Index |
|--------|-------|---|--------|-------|
| a8     |  21   |   | h8     |  28   |
| a7     |  31   |   | h7     |  38   |
| a2     |  81   |   | h2     |  88   |
| a1     |  91   |   | h1     |  98   |
| e1     |  95   |   | e8     |  25   |
| e4     |  65   |   | d7     |  34   |

### Rotated-coordinate conversion

When `current_position` is in black's perspective (after one `move()` call),
the AI's move coordinates come from that rotated index space.  To convert them
to standard algebraic squares:

```python
ai_from_square = coord_to_square(119 - ai_from_coord)
ai_to_square   = coord_to_square(119 - ai_to_coord)
```

To un-rotate a position for display:

```python
display_position = rotated_position.rotate()   # two rotations = identity
board_dict = board_to_dict(display_position)
```

### Valid index ranges

A square index `i` is on the actual 8×8 board if and only if:

```
21 <= i <= 98  AND  i % 10 != 0  AND  i % 10 != 9
```

`coord_to_square` raises `ValueError` for any index outside these bounds.

---

## 3. JSON Serialization (`board_to_dict` in `app.py`)

### Function signature

```python
def board_to_dict(position, include_code=True, use_full_words=False):
```

### Output structure

Returns a `dict` mapping algebraic square names to piece objects:

```json
{
  "e1": { "type": "k", "color": "white", "code": "K" },
  "e8": { "type": "k", "color": "black", "code": "k" },
  "a2": { "type": "p", "color": "white", "code": "P" },
  ...
}
```

| Field  | Type   | Value |
|--------|--------|-------|
| `type` | string | Single-letter piece code, always **lowercase**: `p r n b q k`. If `use_full_words=True` (not used in production routes), expands to `pawn rook knight bishop queen king`. **Frontend expects single letters.** |
| `color`| string | `"white"` or `"black"` — derived from case of the board character (uppercase = white in a non-rotated position) |
| `code` | string | Raw board character: uppercase for white (`P R N B Q K`), lowercase for black (`p r n b q k`). Used by the frontend as the image lookup key. Only present when `include_code=True` (always true in production). |

### Production call site

`/initialize` calls:

```python
board_representation = board_to_dict(current_position, include_code=True)
```

`use_full_words` is omitted (defaults to `False`), so `type` is always a
single letter.  This is what the frontend switch statements expect.

### Important: call only on non-rotated positions

`board_to_dict` assumes the position is in white's perspective.  Always
un-rotate before calling if the position has been through an odd number of
`move()` calls:

```python
# Wrong — rotated board, wrong square names
board_dict = board_to_dict(rotated_position)

# Correct
board_dict = board_to_dict(rotated_position.rotate())
```

---

## 4. Flask Routes (`app.py`)

### `GET /`

Renders `templates/index.html`.  No parameters, no body.

---

### `POST /initialize`

Resets the global game state and returns the starting board.

**Request body (JSON):**

```json
{ "difficulty": "easy" | "medium" | "hard" }
```

`difficulty` defaults to `"medium"` if omitted.

**Response (JSON):**

```json
{
  "board":         { "<square>": { "type": "p", "color": "white", "code": "P" }, ... },
  "legalMoves":    [ { "from": "e2", "to": "e4" }, ... ],
  "gameState":     "active",
  "message":       "Game started with medium difficulty",
  "currentPlayer": "white"
}
```

`legalMoves` contains all legal white moves generated from the initial position
via `format_moves_for_frontend(current_position.gen_moves())`.

**Side effects:** resets `current_position`, `heuristic`, `searcher`,
`move_history`, `current_player`.

---

### `POST /move` (also aliased as `POST /make_move`)

Applies the player's move and the AI's response move.

**Request body (JSON):**

```json
{ "from": "e2", "to": "e4" }
```

**Validation:** the move `(from_coord, to_coord)` must appear in
`current_position.gen_moves()`.  Returns 400 if invalid.

**Processing sequence:**

1. Record `moving_piece = current_position.board[from_coord]` (before rotation).
2. Apply player's move: `new_position = current_position.move(move)`.
   Board is now **rotated to black's perspective**.
3. Run `check_game_result()`.  If game over, rotate back and return early.
4. Run `searcher.search(new_position, secs=1.5)` → `(ai_from_coord, ai_to_coord)`
   in **rotated** coordinate space.
5. Convert AI move to standard squares:
   ```python
   ai_from_square = coord_to_square(119 - ai_from_coord)
   ai_to_square   = coord_to_square(119 - ai_to_coord)
   ```
6. Apply AI's move: `current_position = current_position.move(ai_move)`.
   Board is now **rotated back to white's perspective**.
7. Return board, legal moves, AI move.

**Normal response (JSON):**

```json
{
  "valid":      true,
  "board":      { "<square>": { "type": "...", "color": "...", "code": "..." }, ... },
  "legalMoves": [ { "from": "...", "to": "..." }, ... ],
  "lastMove":   { "from": "<ai_from>", "to": "<ai_to>" },
  "aiMove":     { "from": "<ai_from>", "to": "<ai_to>" },
  "gameResult": null | "Checkmate! White wins" | "Stalemate! ...",
  "check":      false,
  "moves":      [ { "from": "...", "to": "...", "player": "white"|"black", "piece": "p" }, ... ]
}
```

**Error responses:**

| Status | Body |
|--------|------|
| 400 | `{ "error": "Game not initialized", "valid": false }` |
| 400 | `{ "error": "Not your turn", "valid": false }` |
| 400 | `{ "error": "Missing from or to square", "valid": false }` |
| 400 | `{ "error": "Invalid move", "valid": false }` |
| 500 | `{ "error": "...", "valid": false }` |

---

### `POST /evolve`

Runs the genetic algorithm to produce a new AI heuristic tree.

**Request body (JSON):**

```json
{ "generations": 10 }
```

**Response (JSON):**

```json
{ "message": "AI evolved over 10 generations", "success": true }
```

This is a long-running call.  It blocks until evolution finishes.

---

### `GET /test_rendering`

Renders `templates/test_rendering.html`.  Used during development only.

---

## 5. Frontend: `chessboard.js`

### `ChessBoard` class (instantiated in `game.js`)

**Key instance fields:**

| Field | Type | Description |
|-------|------|-------------|
| `boardElement` | `HTMLElement` | The `#chessboard` div |
| `squares` | `{ [squareId]: HTMLElement }` | Map from `"a1"`…`"h8"` to the 64 square divs |
| `boardState` | `{ [squareId]: PieceObj }` | Mirror of the last server-provided board; same structure as the JSON `board` field |
| `legalMoves` | `Array<{ from, to }>` | Legal moves for the current player; populated from `/initialize` and `/move` responses |
| `selectedSquare` | `string \| null` | Currently selected square ID |
| `lastMove` | `{ from, to } \| null` | Squares highlighted as the last move |
| `pieceImages` | `{ [code]: string }` | Maps raw board character codes to SVG paths |

**`pieceImages` map:**

```js
{
  'p': '/static/images/pieces/black-pawn.svg',
  'r': '/static/images/pieces/black-rook.svg',
  'n': '/static/images/pieces/black-knight.svg',
  'b': '/static/images/pieces/black-bishop.svg',
  'q': '/static/images/pieces/black-queen.svg',
  'k': '/static/images/pieces/black-king.svg',
  'P': '/static/images/pieces/white-pawn.svg',
  'R': '/static/images/pieces/white-rook.svg',
  'N': '/static/images/pieces/white-knight.svg',
  'B': '/static/images/pieces/white-bishop.svg',
  'Q': '/static/images/pieces/white-queen.svg',
  'K': '/static/images/pieces/white-king.svg'
}
```

The key is `piece.code` from the JSON response (the raw board character), not
`piece.type`.

### Board creation (`createBoard`)

Creates 64 `<div class="square light|dark">` elements, one per square,
iterating files `a–h` × ranks `8–1` (top-to-bottom, matching white's
perspective).  Each div gets `id` and `data-square-id` set to the square name.
All 64 divs are stored in `this.squares`.

### Rendering (`updateBoardUI`)

```
1. Clear all 64 squares (innerHTML = '').
2. For each entry in boardState:
   a. Look up the square div via this.squares[squareId].
   b. Create <div class="piece white|black"><img src=pieceImages[piece.code]></div>.
   c. Append to the square div.
```

`piece.code` is used for the image — not `piece.type`.  If `code` is missing
or unrecognised, the image src will be `undefined` and the browser will display
a broken-image icon (the piece div is still present in the DOM).

### Move flow

1. User clicks a square → `handleSquareClick` → `handlePlayerSquareClick`.
2. If no selection: call `selectSquare(id)` if the piece is friendly (white).
3. If already selected: call `isLegalMove(from, to)`.
   - Primary check: scan `this.legalMoves` array for `{from, to}`.
   - Hardcoded exception: any same-file rank-2→rank-4 move returns `true`.
   - Fallback: type-based rules using `piece.type` (single letter) for pawns
     and knights.
4. If legal: `makeMove(from, to)`.
   - Optimistic UI update: moves piece in local `boardState` and calls
     `updateBoardUI`.
   - Calls `sendMoveToBackend(from, to, piece, originalBoardState)`.
5. `sendMoveToBackend` POSTs `{ from, to, piece_type, piece_color }` to `/move`.
6. On success response (`data.valid === true`):
   - Update `this.legalMoves` from `data.legalMoves`.
   - Update board from `data.board` (now includes AI's move).
   - Highlight AI's move squares via `updateLastMoveHighlight(data.aiMove.from, data.aiMove.to)`.
   - Dispatch `CustomEvent('moveCompleted', { from, to, aiMove, currentPlayer })`.
   - Dispatch `CustomEvent('gameEnded', { message })` if `data.gameResult` is set.

### Default legal moves (`addDefaultLegalMoves`)

Called when the server provides no legal moves.  Hardcodes standard opening
moves: all pawn single/double advances from ranks 2 and 7, plus the four
knight jumps for each colour.  This is a fallback only; the server always
provides `legalMoves` in the `/initialize` and `/move` responses.

---

## 6. Frontend: `game.js`

Loaded after `chessboard.js`; instantiates `ChessBoard` and wires up all
non-board UI.

### Startup

```
DOMContentLoaded → init() → startNewGame()
```

`startNewGame()` POSTs to `/initialize`, receives the board and legal moves,
calls `chessboard.updateBoard(data.board)` then overwrites
`chessboard.legalMoves` with the result of `generateLegalMoves(data.board)`.

**Important:** `generateLegalMoves` in `game.js` generates moves client-side
from `boardState` using switch cases on `piece.type` (`'p'`, `'r'`, etc.).
Because `piece.type` is always a single letter (with `use_full_words=False`),
these cases match.  If `use_full_words=True` were used, no cases would match
and the function would return `[]`, overwriting the server-provided defaults.

### Custom events

`game.js` listens for events dispatched by `chessboard.js`:

| Event | Detail fields | Handler |
|-------|---------------|---------|
| `moveCompleted` | `{ from, to, aiMove, currentPlayer }` | Adds moves to history, updates button states |
| `moveFailed` | `{ message }` | Shows notification |
| `moveError` | `{ message }` | Shows error notification |
| `gameEnded` | `{ message, winner }` | Sets `gameActive = false`, updates status |
| `checkGameActive` | `{ callback }` | Calls `callback(gameActive, currentPlayer)` |
| `showLoading` | `{ message }` | Shows loading overlay |
| `hideLoading` | — | Hides loading overlay |

---

## 7. AI: Minimax + Genetic Programming

### Heuristic tree (`genetic_programming.py`)

The heuristic used to evaluate positions is a **randomly-generated expression
tree** built from:

| Node type | Class | Behaviour |
|-----------|-------|-----------|
| Operator node | `node` | Applies `fwrapper` function (`add`, `sub`, `mul`, `if`, `gt`) to child results |
| Piece count node | `piecenode` | Returns `position.pieces_dict()[piece_char]` |
| Position evaluation node | `eval_node` | Returns `position.evaluation()` (the engine's built-in score) |
| Constant node | `constnode` | Returns a fixed `float` |

`makerandomtree(pc, state)` builds such a tree recursively.  `evolve(...)` runs
a genetic algorithm (selection → crossover → mutation) over a population of
trees, using `tournament` as the fitness function.

### Search (`minimax.py`)

`Minimax.search(pos, secs)` runs alpha-beta minimax with a time deadline.
It calls `solution(pos, deadline)` which iterates over all legal moves and
picks the one with the highest `value(...)` score.

**Return value:** `(move, score)` where `move = (from_coord, to_coord)` — both
coordinates are in the **current position's coordinate space** (which may be
rotated).

### Global state in `app.py`

```python
current_position  # Position object; white's perspective when it's white's turn
heuristic         # Expression tree node from genetic_programming
searcher          # Minimax instance wrapping heuristic
move_history      # list of { from, to, player, piece } dicts
current_player    # 'white' | 'black'
```

---

## 8. Key Invariants for Future Changes

1. **`board_to_dict` must receive a non-rotated position.**  Call
   `position.rotate()` first if the position has been through an odd number
   of `move()` calls.

2. **AI move coordinates are always in rotated space.**  Convert with
   `coord_to_square(119 - coord)` before sending to the frontend.

3. **Record piece identity before calling `move()`**, because `move()` rotates
   the board, making the original indices invalid.

4. **`piece.type` must be a single letter** (`p r n b q k`).  The frontend
   switch statements, `isLegalMove` fallback, and `highlightFallbackLegalMoves`
   all compare against single letters.  Never pass `use_full_words=True` to
   `board_to_dict` in a route handler.

5. **`piece.code` is what the frontend uses for images**, not `piece.type`.
   `code` is the raw board character (uppercase = white, lowercase = black)
   and matches the keys in `ChessBoard.pieceImages`.

6. **After both the player's move and the AI's move**, `current_position` is
   back in white's perspective (two rotations).  `board_to_dict` and
   `format_moves_for_frontend` can be called directly on it.

7. **The `/move` response uses `valid`, `board`, `legalMoves`, and `aiMove`**
   as field names.  The frontend reads these exact keys (with optional-chaining
   fallbacks for `valid || success` and `board || board_state`).
