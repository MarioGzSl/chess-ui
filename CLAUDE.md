# CLAUDE.md - AI Assistant Development Guide

This document provides comprehensive guidance for AI assistants working with the Chess UI codebase.

## Project Overview

**Chess UI** is a feature-rich chess game application built with Python and pygame, featuring both Player vs Player (PvP) and Player vs Engine modes with real-time Stockfish analysis capabilities.

**Key Features:**
- Player vs Player (PvP) and Player vs Engine game modes
- Stockfish chess engine integration with configurable difficulty (1-20 levels)
- Real-time position analysis and win probability visualization
- Professional dark theme UI with PNG piece graphics
- Move history with algebraic notation
- Save/load game functionality
- Visual indicators for valid moves, captures, and check situations

**Technology Stack:**
- **Language:** Python 3.x
- **UI Framework:** pygame (2.0.0+)
- **Chess Engine:** Stockfish (via stockfish Python library 3.28.0+)
- **Architecture Pattern:** Adapter pattern for engine abstraction

## Codebase Structure

```
chess-ui/
├── chess.py                    # Main game logic and UI (1019 lines)
├── chess_engine_adapter.py     # Engine abstraction layer (405 lines)
├── chess_analysis.py           # Real-time analysis components (327 lines)
├── win_probability_widget.py   # Probability visualization (189 lines)
├── requirements.txt            # Python dependencies
├── install_stockfish.md        # Stockfish installation guide
├── README.md                   # User documentation
├── CLAUDE.md                   # This file - AI assistant guide
├── .gitignore                  # Git ignore patterns
├── assets/
│   └── image.png              # Screenshot for documentation
└── pieces-basic-png/          # Chess piece graphics (PNG files)
    ├── white-*.png
    └── black-*.png
```

### File Responsibilities

**chess.py** - Main Application
- `ChessPiece` class: Piece movement logic, validation, check detection
- `ChessGame` class: Game state, UI rendering, event handling, mode switching
- Entry point: `main()` function with pygame event loop
- Lines of code: ~1019

**chess_engine_adapter.py** - Engine Integration Layer
- `ChessEngineInterface` (ABC): Abstract interface for chess engines
- `StockfishAdapter`: Production engine adapter with UCI protocol
- `MockEngineAdapter`: Testing/fallback engine with random moves
- `ChessEngineManager`: Engine lifecycle and switching management
- Key responsibilities: FEN conversion, UCI move parsing, engine configuration
- Lines of code: ~405

**chess_analysis.py** - Analysis System
- `ChessAnalysisPanel`: Real-time position evaluation display
- `EngineSettingsPanel`: Engine configuration UI
- `ChessAnalysisManager`: Coordinates analysis features
- Provides WDL (Win/Draw/Loss) statistics visualization
- Lines of code: ~327

**win_probability_widget.py** - Visualization
- `WinProbabilityWidget`: Animated probability displays
- Circular charts, horizontal bars, evaluation bars
- Smooth animation transitions
- Lines of code: ~189

## Architecture and Design Patterns

### 1. Adapter Pattern
The codebase uses the **Adapter Pattern** to decouple chess engine implementations from the game logic:

```
ChessGame → ChessEngineManager → ChessEngineInterface
                                       ↑
                          ┌────────────┴────────────┐
                   StockfishAdapter          MockEngineAdapter
```

**Benefits:**
- Easy to add new chess engines
- Testing without Stockfish dependency
- Clean separation of concerns

### 2. Component-Based UI Architecture
UI is organized into distinct components:
- Game board rendering (chess.py:613-647)
- Side panel with move history (chess.py:677-736)
- Analysis panel (chess_analysis.py)
- Difficulty configuration panel (chess.py:886-983)
- Win probability widget (win_probability_widget.py)

### 3. State Management
Game state is centralized in the `ChessGame` class:
```python
self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 board
self.current_player = 'white' | 'black'
self.game_mode = 'PvP' | 'Engine'
self.move_history = []  # Algebraic notation
self.game_over = False
self.winner = None
```

### 4. FEN Notation Conversion
Board state is converted to FEN (Forsyth-Edwards Notation) for engine communication:
- Implementation: `chess_engine_adapter.py:223-272`
- Format: `{board} {active_color} {castling} {en_passant} {halfmove} {fullmove}`
- Example: `"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"`

## Key Components Deep Dive

### ChessPiece Class (chess.py:34-183)

**Attributes:**
- `color`: 'white' or 'black'
- `piece_type`: 'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
- `row`, `col`: Current position (0-7)
- `has_moved`: For castling and pawn double-move logic

**Key Methods:**
- `get_valid_moves(board, check_for_check=True)`: Returns list of (row, col) tuples
- `_is_move_legal(board, to_row, to_col)`: Validates move doesn't expose king
- `_get_{piece}_moves(board)`: Piece-specific movement patterns

**Movement Validation:**
1. Get piece-specific moves (e.g., `_get_pawn_moves()`)
2. Filter moves that would expose own king to check
3. Simulate each move and check if king is under attack
4. Return only legal moves

### ChessGame Class (chess.py:185-983)

**Core Responsibilities:**
1. **Board Management**: 8x8 grid of ChessPiece objects or None
2. **UI Rendering**: pygame-based drawing with dark theme
3. **Event Handling**: Mouse clicks, button interactions
4. **Game Logic**: Turn management, checkmate detection
5. **Mode Switching**: PvP ↔ Engine mode transitions

**Important Methods:**
- `setup_board()`: Initialize starting position (chess.py:280-290)
- `handle_click(pos)`: Process mouse clicks (chess.py:299-370)
- `make_move(from_pos, to_pos)`: Execute move, update state (chess.py:470-508)
- `is_in_check(color)`: Check detection (chess.py:537-553)
- `is_checkmate(color)`: Checkmate detection (chess.py:555-568)
- `draw(screen, font)`: Full UI rendering (chess.py:570-675)

**Algebraic Notation:**
- Implementation: `get_move_notation()` (chess.py:510-527)
- Format: `{piece}{capture}{square}{check/mate}`
- Examples: "e4", "Nf3", "Qxd5+", "Qh7#"

### StockfishAdapter Class (chess_engine_adapter.py:53-289)

**Initialization:**
1. Searches multiple paths for Stockfish binary
2. Falls back to system PATH
3. Sets default depth=10, skill=20
4. Handles initialization failures gracefully

**UCI Communication:**
- `get_best_move(board_state)`: Returns ((from_row, from_col), (to_row, to_col))
- `get_evaluation(board_state)`: Returns dict with 'type', 'value', 'wdl'
- `get_top_moves(board_state, count)`: Returns list of move dictionaries

**Difficulty Configuration:**
- `set_skill_level(1-20)`: Configures UCI_Elo (800-2800)
- Skill < 20: Uses UCI_LimitStrength and Skill Level parameters
- Skill = 20: Maximum strength, no limits

### ChessAnalysisManager (chess_analysis.py:265-327)

**Features:**
- Real-time position evaluation
- Top move suggestions (multi-PV)
- Win/Draw/Loss probability visualization
- Auto-analysis toggle

**Integration Points:**
- Updated via `update(board_state)` after each move
- Draws UI via `draw(screen, panel_x, start_y, panel_width)`
- Coordinates `ChessAnalysisPanel` and `EngineSettingsPanel`

## Development Workflows

### Adding a New Chess Piece

1. **Add movement logic** to `ChessPiece._get_{piece}_moves()`:
   ```python
   def _get_custom_moves(self, board):
       moves = []
       # Add custom movement pattern
       return moves
   ```

2. **Update `get_valid_moves()`** to call new method:
   ```python
   elif self.piece_type == 'custom':
       moves = self._get_custom_moves(board)
   ```

3. **Add piece symbol** in `get_piece_symbol()` (chess.py:292-297):
   ```python
   'custom': '♛'  # Add Unicode symbol
   ```

4. **Add PNG image** to `pieces-basic-png/` directory:
   - `white-custom.png`
   - `black-custom.png`

### Adding a New Chess Engine

1. **Create adapter class** implementing `ChessEngineInterface`:
   ```python
   class NewEngineAdapter(ChessEngineInterface):
       def is_available(self) -> bool: ...
       def get_best_move(self, board_state): ...
       def get_evaluation(self, board_state): ...
       def set_difficulty(self, depth): ...
       def set_skill_level(self, skill): ...
   ```

2. **Register in `ChessEngineManager._initialize_engines()`**:
   ```python
   new_engine = NewEngineAdapter()
   if new_engine.is_available():
       self.engines['new_engine'] = new_engine
   ```

3. **Add UI button** for engine selection (optional)

### Modifying UI Layout

**Key Constants** (chess.py:10-32):
- `BOARD_SIZE = 640`: Chess board pixel size
- `SQUARE_SIZE = 80`: Individual square size
- `PANEL_WIDTH = 250`: Right panel width
- `MENU_HEIGHT = 40`: Top menu bar height

**Color Scheme:**
- Background: `DARK_GRAY = (60, 63, 65)`
- Panel: `LIGHT_GRAY = (43, 43, 43)`
- Text: `TEXT_COLOR = (220, 220, 220)`
- Board: `LIGHT_BROWN = (240, 217, 181)`, `DARK_BROWN = (181, 136, 99)`

**Adding UI Elements:**
1. Define in `setup_buttons()` or render in `draw()`
2. Handle clicks in `handle_click()` or create dedicated handler
3. Update state and trigger re-render

### Save/Load Game State

**Current Implementation** (chess.py:238-267):
- Saves: `move_history`, `current_player`, `game_over`, `winner`
- Format: JSON file (`chess_save.json`)
- Limitation: Move history is saved but not replayed on load

**Improving Save/Load:**
1. Implement move notation parser
2. Replay moves from starting position
3. Restore exact board state
4. Add timestamp and game metadata

## Code Conventions

### Python Style
- **PEP 8 compliant**: Follow standard Python style guidelines
- **Type hints**: Use where applicable (see chess_engine_adapter.py)
- **Docstrings**: Document classes and complex methods
- **Line length**: Prefer ~80-100 characters, max 120

### Naming Conventions
- **Classes**: PascalCase (`ChessGame`, `StockfishAdapter`)
- **Functions/Methods**: snake_case (`get_valid_moves`, `is_in_check`)
- **Constants**: UPPER_SNAKE_CASE (`BOARD_SIZE`, `SQUARE_SIZE`)
- **Private methods**: Leading underscore (`_get_pawn_moves`, `_board_to_fen`)

### Coordinate System
- **Board indices**: (row, col) where row 0 = top, col 0 = left
- **Chess notation**: a-h (columns), 1-8 (rows, bottom to top)
- **Conversion**:
  - Column: `chr(ord('a') + col)`
  - Row: `str(8 - row)`
  - Example: (0, 0) → "a8", (7, 0) → "a1"

### Color Representation
- **Internal**: Strings 'white' or 'black'
- **FEN**: Characters 'w' or 'b'
- **UI**: RGB tuples for rendering

### Move Representation
- **Internal**: Tuple of tuples `((from_row, from_col), (to_row, to_col))`
- **UCI**: String like "e2e4", "g1f3"
- **Algebraic**: String like "e4", "Nf3", "Qxd5+"

## Testing Strategy

### Manual Testing Checklist
1. **PvP Mode:**
   - All piece movements (pawn, rook, knight, bishop, queen, king)
   - Capture moves
   - Check detection
   - Checkmate detection
   - Move history recording

2. **Engine Mode:**
   - Stockfish initialization
   - Engine move generation
   - Difficulty levels (1-20)
   - Engine configuration panel

3. **Analysis Features:**
   - Position evaluation
   - Win probability display
   - WDL statistics
   - Real-time updates

4. **UI Features:**
   - Button interactions
   - Mode switching
   - Save/load functionality
   - Visual indicators (highlights, valid moves)

### Unit Testing (Future Enhancement)
Currently no automated tests exist. Recommended additions:
- FEN conversion correctness (`_board_to_fen`)
- UCI move parsing (`_uci_to_coordinates`)
- Move validation logic
- Checkmate detection edge cases

## Dependencies

### Required Python Packages
```
pygame>=2.0.0      # Game engine and UI rendering
stockfish>=3.28.0  # Stockfish engine Python interface
```

### External Dependencies
- **Stockfish Binary**: Chess engine executable
  - Ubuntu/Debian: `sudo apt install stockfish`
  - See `install_stockfish.md` for detailed instructions
  - Paths checked (in order):
    1. `stockfish` (in PATH)
    2. `/usr/bin/stockfish`
    3. `/usr/local/bin/stockfish`
    4. `/opt/homebrew/bin/stockfish` (macOS)
    5. `C:\Program Files\Stockfish\stockfish.exe` (Windows)
    6. `./stockfish` (local directory)

### Optional Dependencies
- PNG piece images in `pieces-basic-png/` directory
- Falls back to Unicode chess symbols if images missing

## Common Tasks for AI Assistants

### 1. Adding a New Feature

**Before implementing:**
- Read relevant source files completely
- Understand existing patterns and conventions
- Check for similar existing features
- Plan changes across multiple files if needed

**Implementation steps:**
1. Identify which classes/methods need modification
2. Maintain existing code style and patterns
3. Add to existing UI panels rather than creating new ones
4. Test in both PvP and Engine modes
5. Update this CLAUDE.md if architecture changes

### 2. Debugging Issues

**Common issue locations:**
- **Engine not working**: Check `chess_engine_adapter.py:62-93` (initialization)
- **Invalid moves**: Check `ChessPiece.get_valid_moves()` and `_is_move_legal()`
- **UI not rendering**: Check `ChessGame.draw()` and pygame display calls
- **Checkmate not detected**: Check `is_checkmate()` logic
- **FEN conversion errors**: Check `_board_to_fen()` implementation

**Debugging approach:**
1. Add print statements (output goes to console)
2. Check pygame event handling in main loop
3. Verify board state in `self.board`
4. Test with simplified scenarios (fewer pieces)

### 3. Refactoring Code

**Safe refactoring targets:**
- Extract magic numbers to constants
- Split large methods (>50 lines) into smaller functions
- Add type hints to untyped functions
- Improve variable naming for clarity

**Risky changes (avoid without thorough testing):**
- Coordinate system modifications
- FEN conversion logic
- Move validation core logic
- UCI move parsing

### 4. Improving Performance

**Current performance characteristics:**
- UI runs at 60 FPS (clock.tick(60))
- Engine moves have 500ms visual delay
- No caching of engine evaluations
- Board state is recalculated each frame

**Optimization opportunities:**
- Cache engine evaluations for unchanged positions
- Reduce analysis frequency (not every frame)
- Optimize valid move calculation
- Use dirty rectangles for partial redraws

## Important Notes for AI Assistants

### Understanding the Codebase
1. **Read before modifying**: Always read the relevant file completely before making changes
2. **Coordinate system**: Row 0 is top of board, Row 7 is bottom (opposite of chess notation)
3. **Check validation**: Moves are validated by simulating them and checking if king is attacked
4. **FEN conversion**: Critical for engine communication, must be correct

### Best Practices
1. **Preserve existing patterns**: Match the style of surrounding code
2. **Don't over-engineer**: Simple, direct solutions are preferred
3. **Test both modes**: Changes should work in PvP and Engine modes
4. **Maintain separation**: Keep engine logic in adapter, UI in chess.py
5. **Handle errors gracefully**: Engine might not be available, images might be missing

### Code Modification Guidelines
1. **Small changes**: Make incremental, testable changes
2. **Preserve functionality**: Don't break existing features
3. **Add, don't replace**: Extend rather than rewrite when possible
4. **Document complex logic**: Add comments for non-obvious code
5. **Update CLAUDE.md**: If you change architecture or add major features

### Common Pitfalls to Avoid
1. **Coordinate confusion**: Don't mix up (row, col) vs (col, row)
2. **Check validation**: Don't skip the check_for_check parameter
3. **Engine availability**: Always check `is_available()` before using engine
4. **FEN format**: Ensure correct format or engine will reject position
5. **Game state consistency**: Update all related state when making changes

### Git Workflow
- **Current branch**: `claude/add-claude-documentation-4c6Px`
- **Commit messages**: Clear, descriptive messages in imperative mood
- **Push to origin**: Use `git push -u origin <branch-name>`
- **Before committing**: Verify code runs without errors

### Project-Specific Quirks
1. **Mock engine**: Always available as fallback if Stockfish missing
2. **Unicode fallback**: Piece symbols used if PNG images not found
3. **Save format**: JSON saves move history but doesn't replay on load
4. **Animation**: Win probability widget uses smooth transitions
5. **Difficulty scaling**: ELO = 800 + (skill_level * 100)

## Future Enhancement Ideas

### High Priority
- [ ] Implement castling moves
- [ ] Implement en passant captures
- [ ] Pawn promotion to queen/rook/bishop/knight
- [ ] Stalemate detection
- [ ] Threefold repetition detection
- [ ] Fifty-move rule
- [ ] Complete save/load with position replay

### Medium Priority
- [ ] Time controls (clock-based gameplay)
- [ ] Opening book integration
- [ ] Endgame tablebase support
- [ ] Multi-PV analysis display
- [ ] Move takebacks/undo
- [ ] Game export to PGN format
- [ ] Position setup/FEN import

### Low Priority
- [ ] Online multiplayer
- [ ] Puzzle mode
- [ ] Tournament mode
- [ ] Custom themes
- [ ] Sound effects
- [ ] Animated piece movements
- [ ] 3D board view

## Troubleshooting Guide

### Stockfish Not Found
**Symptom**: Engine button disabled, console shows "Stockfish not available"

**Solutions**:
1. Install Stockfish: `sudo apt install stockfish`
2. Check PATH: `which stockfish`
3. Verify installation: `stockfish` (should show version)
4. See `install_stockfish.md` for detailed instructions

### PNG Images Not Loading
**Symptom**: Unicode symbols displayed instead of piece graphics

**Solutions**:
1. Check `pieces-basic-png/` directory exists
2. Verify PNG files are present and properly named
3. Check file permissions (readable)
4. Unicode symbols work as fallback (no action needed)

### Invalid FEN Errors
**Symptom**: Engine moves fail, console shows "Invalid FEN"

**Solutions**:
1. Check `_board_to_fen()` implementation
2. Verify board state is valid (both kings present)
3. Test FEN with external validator
4. Check for board state corruption

### Performance Issues
**Symptom**: Low FPS, laggy UI

**Solutions**:
1. Disable real-time analysis
2. Reduce engine depth
3. Lower difficulty level
4. Close other applications
5. Check pygame version compatibility

## Contact and Resources

### Official Documentation
- **pygame**: https://www.pygame.org/docs/
- **Stockfish**: https://stockfishchess.org/
- **UCI Protocol**: https://www.chessprogramming.org/UCI
- **FEN Notation**: https://www.chessprogramming.org/Forsyth-Edwards_Notation

### Project Repository
- **Main branch**: `main`
- **Development branch**: `claude/add-claude-documentation-4c6Px`
- **Issues**: Report bugs and feature requests via GitHub issues

---

**Last Updated**: 2025-12-29
**Codebase Version**: Based on commits up to `77f5dff`
**Maintained for**: AI assistants (Claude, etc.) working with this codebase

