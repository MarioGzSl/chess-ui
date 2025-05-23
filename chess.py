import pygame
import sys
import os
from chess_engine_adapter import ChessEngineManager
from chess_analysis import ChessAnalysisManager
from win_probability_widget import WinProbabilityWidget

pygame.init()

BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
MARGIN = 30
PANEL_WIDTH = 250
MENU_HEIGHT = 40
WINDOW_WIDTH = BOARD_SIZE + 2 * MARGIN + PANEL_WIDTH
WINDOW_HEIGHT = BOARD_SIZE + 2 * MARGIN + MENU_HEIGHT
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
HIGHLIGHT_COLOR = (255, 255, 100)
VALID_MOVE_COLOR = (100, 255, 100)
CAPTURE_COLOR = (255, 100, 100)
CHECK_COLOR = (255, 50, 50)
PANEL_COLOR = (245, 245, 245)
BORDER_COLOR = (200, 200, 200)
DARK_GRAY = (60, 63, 65)
LIGHT_GRAY = (43, 43, 43)
TEXT_COLOR = (220, 220, 220)
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER = (90, 90, 90)
BUTTON_TEXT = (255, 255, 255)

class ChessPiece:
    def __init__(self, color, piece_type, row, col):
        self.color = color
        self.piece_type = piece_type
        self.row = row
        self.col = col
        self.has_moved = False
    
    def get_valid_moves(self, board, check_for_check=True):
        moves = []
        if self.piece_type == 'pawn':
            moves = self._get_pawn_moves(board)
        elif self.piece_type == 'rook':
            moves = self._get_rook_moves(board)
        elif self.piece_type == 'knight':
            moves = self._get_knight_moves(board)
        elif self.piece_type == 'bishop':
            moves = self._get_bishop_moves(board)
        elif self.piece_type == 'queen':
            moves = self._get_queen_moves(board)
        elif self.piece_type == 'king':
            moves = self._get_king_moves(board)
        
        if not check_for_check:
            return moves
            
        # Filter out moves that would put own king in check
        valid_moves = []
        for move_row, move_col in moves:
            if self._is_move_legal(board, move_row, move_col):
                valid_moves.append((move_row, move_col))
        
        return valid_moves
    
    def _is_move_legal(self, board, to_row, to_col):
        # Simulate the move
        from_row, from_col = self.row, self.col
        captured_piece = board[to_row][to_col]
        
        # Make the move
        board[to_row][to_col] = self
        board[from_row][from_col] = None
        original_row, original_col = self.row, self.col
        self.row, self.col = to_row, to_col
        
        # Check if this move puts own king in check
        king_in_check = False
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color == self.color and piece.piece_type == 'king':
                    # Check if any opponent piece can attack this king
                    opponent_color = 'black' if self.color == 'white' else 'white'
                    for opp_row in range(8):
                        for opp_col in range(8):
                            opp_piece = board[opp_row][opp_col]
                            if opp_piece and opp_piece.color == opponent_color:
                                opp_moves = opp_piece.get_valid_moves(board, check_for_check=False)
                                if (row, col) in opp_moves:
                                    king_in_check = True
                                    break
                        if king_in_check:
                            break
                    break
        
        # Undo the move
        board[from_row][from_col] = self
        board[to_row][to_col] = captured_piece
        self.row, self.col = original_row, original_col
        
        return not king_in_check
    
    def _get_pawn_moves(self, board):
        moves = []
        direction = -1 if self.color == 'white' else 1
        start_row = 6 if self.color == 'white' else 1
        
        # Forward move
        new_row = self.row + direction
        if 0 <= new_row < 8 and board[new_row][self.col] is None:
            moves.append((new_row, self.col))
            # Double move from starting position
            if self.row == start_row and board[new_row + direction][self.col] is None:
                moves.append((new_row + direction, self.col))
        
        # Captures
        for dc in [-1, 1]:
            new_col = self.col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, board):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = self.row + dr * i, self.col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))
                else:
                    if board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))
                    break
        return moves
    
    def _get_knight_moves(self, board):
        moves = []
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in knight_moves:
            new_row, new_col = self.row + dr, self.col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                    moves.append((new_row, new_col))
        return moves
    
    def _get_bishop_moves(self, board):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = self.row + dr * i, self.col + dc * i
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))
                else:
                    if board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))
                    break
        return moves
    
    def _get_queen_moves(self, board):
        return self._get_rook_moves(board) + self._get_bishop_moves(board)
    
    def _get_king_moves(self, board):
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = self.row + dr, self.col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    if board[new_row][new_col] is None or board[new_row][new_col].color != self.color:
                        moves.append((new_row, new_col))
        return moves

class ChessGame:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.capture_moves = []
        self.piece_images = {}
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.buttons = []
        self.game_mode = 'PvP'  # 'PvP' or 'Engine'
        self.engine_manager = ChessEngineManager()
        self.player_color = 'white'  # Player plays as white against engine
        self.show_difficulty_config = False
        self.difficulty_level = 10  # 1-20 scale
        self.analysis_manager = ChessAnalysisManager(self.engine_manager)
        self.win_probability_widget = WinProbabilityWidget()
        self.show_analysis = False
        self.setup_buttons()
        self.load_piece_images()
        self.setup_board()
    
    def setup_buttons(self):
        button_width = 80
        button_height = 30
        button_y = 5
        spacing = 5
        
        self.buttons = [
            {'text': 'PvP', 'rect': pygame.Rect(10, button_y, button_width, button_height), 'action': 'pvp'},
            {'text': 'Engine', 'rect': pygame.Rect(10 + button_width + spacing, button_y, button_width, button_height), 'action': 'engine'},
            {'text': 'Config', 'rect': pygame.Rect(10 + 2 * (button_width + spacing), button_y, button_width, button_height), 'action': 'difficulty'},
            {'text': 'Analysis', 'rect': pygame.Rect(10 + 3 * (button_width + spacing), button_y, button_width, button_height), 'action': 'analysis'},
            {'text': 'Restart', 'rect': pygame.Rect(10 + 4 * (button_width + spacing), button_y, button_width, button_height), 'action': 'restart'},
            {'text': 'Save', 'rect': pygame.Rect(10 + 5 * (button_width + spacing), button_y, button_width, button_height), 'action': 'save'},
            {'text': 'Load', 'rect': pygame.Rect(10 + 6 * (button_width + spacing), button_y, button_width, button_height), 'action': 'load'}
        ]
    
    def restart_game(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        self.capture_moves = []
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.setup_board()
    
    def save_game(self):
        import json
        game_state = {
            'move_history': self.move_history,
            'current_player': self.current_player,
            'game_over': self.game_over,
            'winner': self.winner
        }
        with open('chess_save.json', 'w') as f:
            json.dump(game_state, f)
    
    def load_game(self):
        import json
        try:
            with open('chess_save.json', 'r') as f:
                game_state = json.load(f)
            
            self.restart_game()
            
            # Replay moves
            for move_notation in game_state['move_history']:
                # This is a simplified load - in a full implementation you'd need to parse notation
                pass
            
            self.current_player = game_state['current_player']
            self.game_over = game_state['game_over']
            self.winner = game_state['winner']
            self.move_history = game_state['move_history']
        except FileNotFoundError:
            pass  # No save file exists
    
    def load_piece_images(self):
        pieces_dir = "pieces-basic-png"
        for color in ['white', 'black']:
            for piece_type in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
                filename = f"{color}-{piece_type}.png"
                filepath = os.path.join(pieces_dir, filename)
                if os.path.exists(filepath):
                    image = pygame.image.load(filepath)
                    image = pygame.transform.scale(image, (SQUARE_SIZE - 10, SQUARE_SIZE - 10))
                    self.piece_images[(color, piece_type)] = image
    
    def setup_board(self):
        # Pawns
        for col in range(8):
            self.board[1][col] = ChessPiece('black', 'pawn', 1, col)
            self.board[6][col] = ChessPiece('white', 'pawn', 6, col)
        
        # Other pieces
        piece_order = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for col in range(8):
            self.board[0][col] = ChessPiece('black', piece_order[col], 0, col)
            self.board[7][col] = ChessPiece('white', piece_order[col], 7, col)
    
    def get_piece_symbol(self, piece):
        symbols = {
            'white': {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
            'black': {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
        }
        return symbols[piece.color][piece.piece_type]
    
    def handle_click(self, pos):
        # Check button clicks first
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if button['action'] == 'restart':
                    self.restart_game()
                elif button['action'] == 'save':
                    self.save_game()
                elif button['action'] == 'load':
                    self.load_game()
                elif button['action'] == 'pvp':
                    self.game_mode = 'PvP'
                    self.restart_game()
                elif button['action'] == 'engine':
                    if self.engine_manager.is_engine_available('stockfish'):
                        self.game_mode = 'Engine'
                        self.restart_game()
                    else:
                        print("Stockfish not available. Please install Stockfish first.")
                        print("See install_stockfish.md for instructions.")
                elif button['action'] == 'difficulty':
                    self.show_difficulty_config = not self.show_difficulty_config
                elif button['action'] == 'analysis':
                    self.show_analysis = not self.show_analysis
                    if self.show_analysis:
                        self.analysis_manager.toggle_analysis()
                return
        
        if self.game_over:
            return
        
        # Check difficulty config clicks
        if self.show_difficulty_config:
            difficulty_handled = self.handle_difficulty_click(pos)
            if difficulty_handled:
                return
        
        # In engine mode, only allow player moves when it's their turn
        if self.game_mode == 'Engine' and self.current_player != self.player_color:
            return
            
        # Adjust for margin and menu
        board_x = pos[0] - MARGIN
        board_y = pos[1] - MARGIN - MENU_HEIGHT
        
        if board_x < 0 or board_y < 0 or board_x >= BOARD_SIZE or board_y >= BOARD_SIZE:
            return
            
        col = board_x // SQUARE_SIZE
        row = board_y // SQUARE_SIZE
        
        if self.selected_piece is None:
            piece = self.board[row][col]
            if piece is not None and piece.color == self.current_player:
                self.selected_piece = piece
                self.selected_pos = (row, col)
                self.valid_moves = piece.get_valid_moves(self.board)
                self.capture_moves = [(r, c) for r, c in self.valid_moves 
                                    if self.board[r][c] is not None]
        else:
            if (row, col) in self.valid_moves:
                self.make_move(self.selected_pos, (row, col))
                self.current_player = 'black' if self.current_player == 'white' else 'white'
                
                # After player move in engine mode, trigger engine move
                if self.game_mode == 'Engine' and not self.game_over:
                    self.make_engine_move()
            
            self.selected_piece = None
            self.selected_pos = None
            self.valid_moves = []
            self.capture_moves = []
    
    def make_engine_move(self):
        if self.game_mode != 'Engine' or self.current_player == self.player_color:
            return
        
        engine = self.engine_manager.get_active_engine()
        move_coords = engine.get_best_move(self)
        
        if move_coords:
            from_pos, to_pos = move_coords
            # Validate the move is legal
            piece = self.board[from_pos[0]][from_pos[1]]
            if piece and piece.color == self.current_player:
                valid_moves = piece.get_valid_moves(self.board)
                if to_pos in valid_moves:
                    self.make_move(from_pos, to_pos)
                    self.current_player = 'black' if self.current_player == 'white' else 'white'
    
    def handle_difficulty_click(self, pos):
        """Handle clicks in difficulty configuration panel"""
        # Get difficulty panel area
        panel_x = BOARD_SIZE + 2 * MARGIN
        panel_y = MENU_HEIGHT + 100
        
        # Difficulty slider area
        slider_x = panel_x + 20
        slider_y = panel_y + 80
        slider_width = 180
        slider_height = 20
        
        if (slider_x <= pos[0] <= slider_x + slider_width and
            slider_y <= pos[1] <= slider_y + slider_height):
            # Calculate new difficulty level
            relative_x = pos[0] - slider_x
            new_difficulty = int((relative_x / slider_width) * 20) + 1
            new_difficulty = max(1, min(20, new_difficulty))
            
            if new_difficulty != self.difficulty_level:
                self.difficulty_level = new_difficulty
                self.apply_difficulty_settings()
            return True
        
        # Preset buttons area
        preset_y = panel_y + 120
        button_width = 80
        button_height = 25
        spacing = 10
        
        presets = [
            {'name': 'Easy', 'level': 5},
            {'name': 'Medium', 'level': 10},
            {'name': 'Hard', 'level': 15},
            {'name': 'Maximum', 'level': 20}
        ]
        
        for i, preset in enumerate(presets):
            button_x = panel_x + 10 + i * (button_width + spacing)
            if (button_x <= pos[0] <= button_x + button_width and
                preset_y <= pos[1] <= preset_y + button_height):
                self.difficulty_level = preset['level']
                self.apply_difficulty_settings()
                return True
        
        return False
    
    def apply_difficulty_settings(self):
        """Apply difficulty settings to the engine"""
        engine = self.engine_manager.get_active_engine()
        if engine and hasattr(engine, 'set_skill_level'):
            engine.set_skill_level(self.difficulty_level)
            print(f"Difficulty set to level {self.difficulty_level}/20")
    
    def get_difficulty_name(self):
        """Get human-readable difficulty name"""
        if self.difficulty_level <= 5:
            return "Beginner"
        elif self.difficulty_level <= 10:
            return "Intermediate"
        elif self.difficulty_level <= 15:
            return "Advanced"
        else:
            return "Master"
    
    def update_position_analysis(self):
        """Update position analysis and win probabilities"""
        if not self.show_analysis:
            return
        
        # Update analysis manager
        self.analysis_manager.update(self)
        
        # Get evaluation for probability widget
        engine = self.engine_manager.get_active_engine()
        if engine and engine.is_available():
            evaluation = engine.get_evaluation(self)
            if 'wdl' in evaluation:
                self.win_probability_widget.update_probabilities(evaluation['wdl'])
                self.win_probability_widget.update_animation()
    
    def make_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        # Record the move in algebraic notation
        move_notation = self.get_move_notation(piece, from_pos, to_pos, captured_piece)
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        piece.row = to_row
        piece.col = to_col
        piece.has_moved = True
        
        # Add move to history
        self.move_history.append(move_notation)
        
        # Check for checkmate after switching players
        next_player = 'black' if self.current_player == 'white' else 'white'
        
        # Check if opponent is in check after this move
        if self.is_in_check(next_player):
            if self.is_checkmate(next_player):
                self.game_over = True
                self.winner = self.current_player
                # Add checkmate notation
                if len(self.move_history) > 0:
                    self.move_history[-1] += '#'
            else:
                # Add check notation
                if len(self.move_history) > 0:
                    self.move_history[-1] += '+'
        
        # Update analysis after each move
        if self.show_analysis:
            self.update_position_analysis()
    
    def get_move_notation(self, piece, from_pos, to_pos, captured_piece):
        _, from_col = from_pos
        to_row, to_col = to_pos
        
        # Convert positions to algebraic notation
        to_square = chr(ord('a') + to_col) + str(8 - to_row)
        
        piece_symbol = '' if piece.piece_type == 'pawn' else piece.piece_type[0].upper()
        capture_symbol = 'x' if captured_piece else ''
        
        if piece.piece_type == 'pawn' and captured_piece:
            notation = f"{chr(ord('a') + from_col)}{capture_symbol}{to_square}"
        else:
            notation = f"{piece_symbol}{capture_symbol}{to_square}"
        
        # Check if this move puts opponent in check
        # We'll add the check symbol after the move is made
        return notation
    
    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color and piece.piece_type == 'king':
                    return (row, col)
        return None
    
    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        king_row, king_col = king_pos
        
        # Check if any opponent piece can attack the king
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    valid_moves = piece.get_valid_moves(self.board, check_for_check=False)
                    if (king_row, king_col) in valid_moves:
                        return True
        return False
    
    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        
        # Try all possible moves for the player in check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    valid_moves = piece.get_valid_moves(self.board, check_for_check=True)
                    if len(valid_moves) > 0:
                        return False
        
        return True
    
    def draw(self, screen, font):
        # Clear screen with dark background
        screen.fill(DARK_GRAY)
        
        # Draw menu bar
        self.draw_menu_bar(screen)
        
        # Draw board notation
        notation_font = pygame.font.Font(None, 24)
        
        # Draw column letters (a-h)
        for col in range(8):
            letter = chr(ord('a') + col)
            text = notation_font.render(letter, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, MENU_HEIGHT + MARGIN // 2))
            screen.blit(text, text_rect)
            text_rect = text.get_rect(center=(MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, WINDOW_HEIGHT - MARGIN // 2))
            screen.blit(text, text_rect)
        
        # Draw row numbers (1-8)
        for row in range(8):
            number = str(8 - row)
            text = notation_font.render(number, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(MARGIN // 2, MENU_HEIGHT + MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2))
            screen.blit(text, text_rect)
        
        # Draw side panel with dark theme
        panel_x = BOARD_SIZE + 2 * MARGIN
        panel_rect = pygame.Rect(panel_x, MENU_HEIGHT, PANEL_WIDTH, WINDOW_HEIGHT - MENU_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, panel_rect)
        pygame.draw.line(screen, BORDER_COLOR, (panel_x, MENU_HEIGHT), (panel_x, WINDOW_HEIGHT), 2)
        
        # Draw move history
        y_pos = self.draw_move_history(screen, panel_x)
        
        # Draw analysis if enabled
        if self.show_analysis:
            y_pos = self.draw_analysis_panel(screen, panel_x, y_pos)
        
        # Draw difficulty configuration if shown
        if self.show_difficulty_config:
            self.draw_difficulty_config(screen, panel_x)
        
        # Draw board squares
        for row in range(8):
            for col in range(8):
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
                rect = pygame.Rect(MARGIN + col * SQUARE_SIZE, MENU_HEIGHT + MARGIN + row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                pygame.draw.rect(screen, color, rect)
                
                if self.selected_pos == (row, col):
                    pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 5)
                
                # Check if this square contains a king in check
                piece = self.board[row][col]
                if piece and piece.piece_type == 'king' and self.is_in_check(piece.color):
                    pygame.draw.rect(screen, CHECK_COLOR, rect, 8)
                
                if (row, col) in self.capture_moves:
                    pygame.draw.rect(screen, CAPTURE_COLOR, rect, 5)
                elif (row, col) in self.valid_moves:
                    pygame.draw.circle(screen, VALID_MOVE_COLOR, 
                                     (MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2, 
                                      MENU_HEIGHT + MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2), 10)
                
                if piece is not None:
                    image_key = (piece.color, piece.piece_type)
                    if image_key in self.piece_images:
                        image = self.piece_images[image_key]
                        image_rect = image.get_rect(center=(MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                          MENU_HEIGHT + MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(image, image_rect)
                    else:
                        symbol = self.get_piece_symbol(piece)
                        text = font.render(symbol, True, BLACK)
                        text_rect = text.get_rect(center=(MARGIN + col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                        MENU_HEIGHT + MARGIN + row * SQUARE_SIZE + SQUARE_SIZE // 2))
                        screen.blit(text, text_rect)
        
        # Draw game over message with better styling
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (MARGIN, MENU_HEIGHT + MARGIN))
            
            # Winner announcement with shadow effect
            winner_text = f"CHECKMATE!"
            subtext = f"{self.winner.upper()} WINS"
            
            # Shadow for main text
            shadow_surface = font.render(winner_text, True, BLACK)
            shadow_rect = shadow_surface.get_rect(center=((BOARD_SIZE + 2 * MARGIN) // 2 + 2, (WINDOW_HEIGHT + MENU_HEIGHT) // 2 - 20 + 2))
            screen.blit(shadow_surface, shadow_rect)
            
            # Main text
            text_surface = font.render(winner_text, True, WHITE)
            text_rect = text_surface.get_rect(center=((BOARD_SIZE + 2 * MARGIN) // 2, (WINDOW_HEIGHT + MENU_HEIGHT) // 2 - 20))
            screen.blit(text_surface, text_rect)
            
            # Subtext
            subtitle_font = pygame.font.Font(None, 48)
            subtitle_surface = subtitle_font.render(subtext, True, (255, 215, 0))  # Gold color
            subtitle_rect = subtitle_surface.get_rect(center=((BOARD_SIZE + 2 * MARGIN) // 2, (WINDOW_HEIGHT + MENU_HEIGHT) // 2 + 30))
            screen.blit(subtitle_surface, subtitle_rect)
    
    def draw_move_history(self, screen, panel_x):
        title_font = pygame.font.Font(None, 32)
        move_font = pygame.font.Font(None, 22)
        small_font = pygame.font.Font(None, 20)
        
        y_pos = MENU_HEIGHT + 25
        
        # Title
        title_text = title_font.render("Move History", True, TEXT_COLOR)
        screen.blit(title_text, (panel_x + 15, y_pos))
        y_pos += 40
        
        # Current player indicator with better styling
        if self.game_over:
            player_text = f"Winner: {self.winner.upper()}"
            color = (100, 255, 100)  # Green for winner
        else:
            if self.game_mode == 'Engine':
                if self.current_player == self.player_color:
                    player_text = f"Your turn ({self.current_player.upper()})"
                else:
                    player_text = f"Engine thinking..."
            else:
                player_text = f"Turn: {self.current_player.upper()}"
            color = (100, 150, 255) if self.current_player == 'white' else (255, 150, 100)
        
        player_surface = move_font.render(player_text, True, color)
        screen.blit(player_surface, (panel_x + 15, y_pos))
        y_pos += 25
        
        # Draw separator line
        pygame.draw.line(screen, BORDER_COLOR, (panel_x + 15, y_pos), (panel_x + PANEL_WIDTH - 15, y_pos), 1)
        y_pos += 15
        max_visible_moves = 40
        start_index = max(0, len(self.move_history) - max_visible_moves)
        
        # Display moves in pairs on the same line
        i = start_index
        while i < len(self.move_history):
            move_number = (i // 2) + 1
            white_move = self.move_history[i] if i < len(self.move_history) else ""
            black_move = self.move_history[i + 1] if i + 1 < len(self.move_history) else ""
            
            # Create the line text
            if black_move:
                line_text = f"{move_number}. {white_move} {black_move}"
            else:
                line_text = f"{move_number}. {white_move}"
            
            move_surface = small_font.render(line_text, True, TEXT_COLOR)
            screen.blit(move_surface, (panel_x + 15, y_pos))
            
            y_pos += 22
            i += 2
            
            # Stop if we run out of space
            if y_pos > WINDOW_HEIGHT - 200:
                break
        
        return y_pos + 10
    
    def draw_analysis_panel(self, screen, panel_x, start_y):
        """Draw real-time analysis panel"""
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 18)
        
        y_pos = start_y
        
        # Analysis title
        title_text = font.render("Real-time Analysis", True, TEXT_COLOR)
        screen.blit(title_text, (panel_x + 15, y_pos))
        y_pos += 30
        
        # Draw separator line
        pygame.draw.line(screen, BORDER_COLOR, (panel_x + 15, y_pos), (panel_x + PANEL_WIDTH - 15, y_pos), 1)
        y_pos += 10
        
        # Get current evaluation
        engine = self.engine_manager.get_active_engine()
        if engine and engine.is_available():
            evaluation = engine.get_evaluation(self)
            
            # Position evaluation
            if evaluation:
                eval_text = self._format_evaluation_simple(evaluation)
                eval_surface = small_font.render(f"Evaluation: {eval_text}", True, TEXT_COLOR)
                screen.blit(eval_surface, (panel_x + 15, y_pos))
                y_pos += 20
                
                # Win probabilities with visual bars
                if 'wdl' in evaluation:
                    y_pos = self._draw_compact_probabilities(screen, panel_x, y_pos, evaluation['wdl'], small_font)
        
        return y_pos + 10
    
    def _format_evaluation_simple(self, evaluation):
        """Format evaluation for compact display"""
        if 'type' in evaluation:
            if evaluation['type'] == 'cp':
                cp = evaluation.get('value', 0)
                return f"{cp/100:+.2f}"
            elif evaluation['type'] == 'mate':
                mate = evaluation.get('value', 0)
                return f"Mate in {abs(mate)}"
        return "0.00"
    
    def _draw_compact_probabilities(self, screen, panel_x, start_y, wdl_stats, font):
        """Draw compact probability visualization"""
        if len(wdl_stats) != 3:
            return start_y
        
        wins, draws, losses = wdl_stats
        total = wins + draws + losses
        
        if total == 0:
            return start_y
        
        # Calculate percentages
        win_pct = (wins / total) * 100
        draw_pct = (draws / total) * 100
        loss_pct = (losses / total) * 100
        
        y_pos = start_y
        
        # Title
        title = font.render("Probabilities:", True, TEXT_COLOR)
        screen.blit(title, (panel_x + 15, y_pos))
        y_pos += 20
        
        # Compact bar
        bar_width = PANEL_WIDTH - 40
        bar_height = 15
        bar_x = panel_x + 15
        
        # Background
        bg_rect = pygame.Rect(bar_x, y_pos, bar_width, bar_height)
        pygame.draw.rect(screen, (30, 30, 30), bg_rect)
        pygame.draw.rect(screen, BORDER_COLOR, bg_rect, 1)
        
        # Segments
        current_x = bar_x
        
        # White segment
        white_width = int((win_pct / 100) * bar_width)
        if white_width > 0:
            white_rect = pygame.Rect(current_x, y_pos, white_width, bar_height)
            pygame.draw.rect(screen, (200, 200, 200), white_rect)
            current_x += white_width
        
        # Draw segment
        draw_width = int((draw_pct / 100) * bar_width)
        if draw_width > 0:
            draw_rect = pygame.Rect(current_x, y_pos, draw_width, bar_height)
            pygame.draw.rect(screen, (200, 200, 0), draw_rect)
            current_x += draw_width
        
        # Black segment
        black_width = int((loss_pct / 100) * bar_width)
        if black_width > 0:
            black_rect = pygame.Rect(current_x, y_pos, black_width, bar_height)
            pygame.draw.rect(screen, (80, 80, 80), black_rect)
        
        y_pos += 25
        
        # Percentage text
        prob_text = f"W:{win_pct:.0f}% D:{draw_pct:.0f}% B:{loss_pct:.0f}%"
        prob_surface = font.render(prob_text, True, TEXT_COLOR)
        screen.blit(prob_surface, (panel_x + 15, y_pos))
        y_pos += 20
        
        return y_pos
    
    def draw_menu_bar(self, screen):
        # Draw menu bar background
        menu_rect = pygame.Rect(0, 0, WINDOW_WIDTH, MENU_HEIGHT)
        pygame.draw.rect(screen, LIGHT_GRAY, menu_rect)
        pygame.draw.line(screen, BORDER_COLOR, (0, MENU_HEIGHT), (WINDOW_WIDTH, MENU_HEIGHT), 2)
        
        # Draw buttons
        button_font = pygame.font.Font(None, 20)
        for button in self.buttons:
            # Highlight active mode buttons
            if button['action'] == 'pvp' and self.game_mode == 'PvP':
                button_color = (100, 150, 100)
            elif button['action'] == 'engine' and self.game_mode == 'Engine':
                button_color = (100, 150, 100)
            elif button['action'] == 'difficulty' and self.show_difficulty_config:
                button_color = (150, 150, 100)
            elif button['action'] == 'analysis' and self.show_analysis:
                button_color = (100, 150, 150)
            else:
                button_color = BUTTON_COLOR
            
            # Disable engine button if Stockfish not available
            if button['action'] == 'engine' and not self.engine_manager.is_engine_available('stockfish'):
                button_color = (50, 50, 50)
                text_color = (100, 100, 100)
            else:
                text_color = BUTTON_TEXT
            
            # Draw button background
            pygame.draw.rect(screen, button_color, button['rect'])
            pygame.draw.rect(screen, BORDER_COLOR, button['rect'], 1)
            
            # Draw button text
            text_surface = button_font.render(button['text'], True, text_color)
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
    
    def draw_difficulty_config(self, screen, panel_x):
        """Draw difficulty configuration panel"""
        config_y = MENU_HEIGHT + 100
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        
        # Background for config panel
        config_rect = pygame.Rect(panel_x + 5, config_y, PANEL_WIDTH - 10, 200)
        pygame.draw.rect(screen, (50, 50, 50), config_rect)
        pygame.draw.rect(screen, BORDER_COLOR, config_rect, 2)
        
        # Title
        title = font.render("Difficulty Configuration", True, TEXT_COLOR)
        screen.blit(title, (panel_x + 10, config_y + 10))
        
        # Current difficulty level
        difficulty_name = self.get_difficulty_name()
        difficulty_text = small_font.render(f"Level: {self.difficulty_level}/20 ({difficulty_name})", True, TEXT_COLOR)
        screen.blit(difficulty_text, (panel_x + 10, config_y + 35))
        
        # Difficulty slider
        slider_x = panel_x + 20
        slider_y = config_y + 60
        slider_width = 180
        slider_height = 20
        
        # Slider background
        slider_bg = pygame.Rect(slider_x, slider_y, slider_width, slider_height)
        pygame.draw.rect(screen, (30, 30, 30), slider_bg)
        pygame.draw.rect(screen, BORDER_COLOR, slider_bg, 1)
        
        # Slider fill
        fill_width = int((self.difficulty_level / 20) * slider_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(slider_x, slider_y, fill_width, slider_height)
            
            # Color based on difficulty
            if self.difficulty_level <= 5:
                color = (100, 255, 100)  # Green for easy
            elif self.difficulty_level <= 10:
                color = (255, 255, 100)  # Yellow for medium
            elif self.difficulty_level <= 15:
                color = (255, 150, 100)  # Orange for hard
            else:
                color = (255, 100, 100)  # Red for maximum
            
            pygame.draw.rect(screen, color, fill_rect)
        
        # Slider handle
        handle_x = slider_x + int((self.difficulty_level / 20) * slider_width) - 5
        handle_rect = pygame.Rect(handle_x, slider_y - 2, 10, slider_height + 4)
        pygame.draw.rect(screen, WHITE, handle_rect)
        pygame.draw.rect(screen, BLACK, handle_rect, 1)
        
        # Preset buttons
        preset_y = config_y + 100
        button_width = 50
        button_height = 25
        spacing = 5
        
        presets = [
            {'name': 'Easy', 'level': 5, 'color': (100, 255, 100)},
            {'name': 'Medium', 'level': 10, 'color': (255, 255, 100)},
            {'name': 'Hard', 'level': 15, 'color': (255, 150, 100)},
            {'name': 'Maximum', 'level': 20, 'color': (255, 100, 100)}
        ]
        
        for i, preset in enumerate(presets):
            button_x = panel_x + 10 + i * (button_width + spacing)
            button_rect = pygame.Rect(button_x, preset_y, button_width, button_height)
            
            # Highlight if current level
            if self.difficulty_level == preset['level']:
                pygame.draw.rect(screen, preset['color'], button_rect)
                text_color = BLACK
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
                text_color = BUTTON_TEXT
            
            pygame.draw.rect(screen, BORDER_COLOR, button_rect, 1)
            
            # Button text
            button_font = pygame.font.Font(None, 16)
            text = button_font.render(preset['name'], True, text_color)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)
        
        # ELO estimation
        estimated_elo = 800 + (self.difficulty_level * 100)
        elo_text = small_font.render(f"Estimated ELO: ~{estimated_elo}", True, TEXT_COLOR)
        screen.blit(elo_text, (panel_x + 10, config_y + 140))
        
        # Engine info
        engine = self.engine_manager.get_active_engine()
        if hasattr(engine, 'get_engine_info'):
            info = engine.get_engine_info()
            engine_text = small_font.render(f"Engine: {info.get('name', 'N/A')}", True, TEXT_COLOR)
            screen.blit(engine_text, (panel_x + 10, config_y + 160))

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Game - PvP vs Engine")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 72)
    
    game = ChessGame()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.handle_click(event.pos)
        
        # Auto-make engine move if it's engine's turn
        if game.game_mode == 'Engine' and game.current_player != game.player_color and not game.game_over:
            pygame.time.wait(500)  # Small delay for visual feedback
            game.make_engine_move()
        
        # Update win probability widget animation
        if game.show_analysis:
            game.win_probability_widget.update_animation()
        
        game.draw(screen, font)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()