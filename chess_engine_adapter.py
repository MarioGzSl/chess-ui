"""
Chess Engine Adapter
Implements the Adapter pattern to separate engine logic from UI
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from chess import ChessGame

try:
    from stockfish import Stockfish
    STOCKFISH_AVAILABLE = True
except ImportError:
    STOCKFISH_AVAILABLE = False


class ChessEngineInterface(ABC):
    """Abstract interface for chess engines"""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the engine is available and ready"""
        pass
    
    @abstractmethod
    def get_best_move(self, board_state: 'ChessGame') -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get the best move for the current position"""
        pass
    
    @abstractmethod
    def get_top_moves(self, board_state: 'ChessGame', count: int = 3) -> List[Dict[str, Any]]:
        """Get the top N moves with their evaluations"""
        pass
    
    @abstractmethod
    def get_evaluation(self, board_state: 'ChessGame') -> Dict[str, Any]:
        """Get position evaluation"""
        pass
    
    @abstractmethod
    def set_difficulty(self, depth: int) -> None:
        """Set the thinking depth/difficulty of the engine"""
        pass
    
    @abstractmethod
    def set_skill_level(self, skill: int) -> None:
        """Set engine skill level (0-20)"""
        pass


class StockfishAdapter(ChessEngineInterface):
    """Adapter for the Stockfish chess engine"""
    
    def __init__(self):
        self.engine = None
        self.current_depth = 10
        self.current_skill = 20
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """Initialize the Stockfish engine with fallback paths"""
        if not STOCKFISH_AVAILABLE:
            print("Stockfish library not available")
            return
        
        stockfish_paths = [
            "stockfish",  # If in PATH
            "/usr/bin/stockfish",
            "/usr/local/bin/stockfish",
            "/opt/homebrew/bin/stockfish",  # macOS Homebrew
            "C:\\Program Files\\Stockfish\\stockfish.exe",  # Windows
            "./stockfish",  # Local directory
        ]
        
        for path in stockfish_paths:
            try:
                self.engine = Stockfish(path=path)
                self.engine.set_depth(10)
                print(f"Stockfish initialized with path: {path}")
                return
            except Exception:
                continue
        
        # Try without path as last resort
        try:
            self.engine = Stockfish()
            self.engine.set_depth(10)
            print("Stockfish initialized without explicit path")
        except Exception as e:
            print(f"Failed to initialize Stockfish: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if Stockfish is available"""
        return self.engine is not None
    
    def get_best_move(self, board_state) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get the best move from Stockfish"""
        if not self.engine:
            return None
        
        try:
            # Convert board to FEN
            fen = self._board_to_fen(board_state)
            
            # Validate FEN
            if not self.engine.is_fen_valid(fen):
                print(f"Invalid FEN: {fen}")
                return None
            
            # Set position and get move
            self.engine.set_fen_position(fen)
            uci_move = self.engine.get_best_move()
            
            if uci_move:
                return self._uci_to_coordinates(uci_move)
            
        except Exception as e:
            print(f"Error getting Stockfish move: {e}")
        
        return None
    
    def get_top_moves(self, board_state, count: int = 3) -> List[Dict[str, Any]]:
        """Get the top N moves with their evaluations"""
        if not self.engine:
            return []
        
        try:
            fen = self._board_to_fen(board_state)
            if not self.engine.is_fen_valid(fen):
                return []
            
            self.engine.set_fen_position(fen)
            top_moves = self.engine.get_top_moves(count)
            
            # Convert to our format
            result = []
            for move_data in top_moves:
                move_coords = self._uci_to_coordinates(move_data['Move'])
                if move_coords:
                    result.append({
                        'move': move_coords,
                        'uci': move_data['Move'],
                        'centipawn': move_data.get('Centipawn'),
                        'mate': move_data.get('Mate')
                    })
            
            return result
        except Exception as e:
            print(f"Error getting top moves: {e}")
            return []
    
    def get_evaluation(self, board_state) -> Dict[str, Any]:
        """Get position evaluation"""
        if not self.engine:
            return {}
        
        try:
            fen = self._board_to_fen(board_state)
            if not self.engine.is_fen_valid(fen):
                return {}
            
            self.engine.set_fen_position(fen)
            evaluation = self.engine.get_evaluation()
            
            # Get WDL stats if available
            try:
                wdl = self.engine.get_wdl_stats()
                evaluation['wdl'] = wdl
            except:
                pass
            
            return evaluation
        except Exception as e:
            print(f"Error getting evaluation: {e}")
            return {}
    
    def set_difficulty(self, depth: int) -> None:
        """Set the thinking depth"""
        if self.engine:
            self.current_depth = max(1, min(depth, 20))  # Clamp between 1-20
            self.engine.set_depth(self.current_depth)
    
    def set_skill_level(self, skill: int) -> None:
        """Set engine skill level (0-20)"""
        if self.engine:
            self.current_skill = max(0, min(skill, 20))  # Clamp between 0-20
            # Configure Stockfish for skill level
            if skill < 20:
                # Lower skill settings
                self.engine.update_engine_parameters({
                    "Skill Level": skill,
                    "UCI_LimitStrength": True,
                    "UCI_Elo": 800 + (skill * 100)  # Scale from 800 to 2800 ELO
                })
            else:
                # Maximum strength
                self.engine.update_engine_parameters({
                    "UCI_LimitStrength": False
                })
                
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine configuration info"""
        return {
            'name': 'Stockfish',
            'depth': self.current_depth,
            'skill': self.current_skill,
            'available': self.is_available(),
            'version': self._get_version()
        }
    
    def _get_version(self) -> str:
        """Get Stockfish version"""
        if self.engine:
            try:
                return str(self.engine.get_stockfish_major_version())
            except:
                return "Unknown"
        return "Not available"
    
    def _board_to_fen(self, board_state) -> str:
        """Convert internal board representation to FEN notation"""
        board = board_state.board
        current_player = board_state.current_player
        move_history = board_state.move_history
        
        # Convert board to FEN
        fen_rows = []
        for row in board:
            fen_row = ""
            empty_count = 0
            for piece in row:
                if piece is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    
                    # Map piece types to FEN notation
                    piece_map = {
                        'king': 'K',
                        'queen': 'Q', 
                        'rook': 'R',
                        'bishop': 'B',
                        'knight': 'N',
                        'pawn': 'P'
                    }
                    
                    piece_char = piece_map.get(piece.piece_type, 'P')
                    
                    if piece.color == 'black':
                        piece_char = piece_char.lower()
                    
                    fen_row += piece_char
            
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        
        board_fen = '/'.join(fen_rows)
        
        # Add game state info
        active_color = 'w' if current_player == 'white' else 'b'
        castling = '-'  # Simplified - no castling for now
        en_passant = '-'   # Simplified - no en passant
        halfmove = '0'     # Simplified
        fullmove = str(len(move_history) // 2 + 1)
        
        return f"{board_fen} {active_color} {castling} {en_passant} {halfmove} {fullmove}"
    
    def _uci_to_coordinates(self, uci_move: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Convert UCI move notation to board coordinates"""
        if not uci_move or len(uci_move) != 4:
            return None
        
        from_col = ord(uci_move[0]) - ord('a')
        from_row = 8 - int(uci_move[1])
        to_col = ord(uci_move[2]) - ord('a')
        to_row = 8 - int(uci_move[3])
        
        # Validate coordinates
        if not (0 <= from_row < 8 and 0 <= from_col < 8 and 
                0 <= to_row < 8 and 0 <= to_col < 8):
            return None
        
        return ((from_row, from_col), (to_row, to_col))


class MockEngineAdapter(ChessEngineInterface):
    """Mock engine for testing or when no real engine is available"""
    
    def __init__(self):
        self.depth = 5
    
    def is_available(self) -> bool:
        return True
    
    def get_best_move(self, board_state) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Return a random valid move (mock implementation)"""
        import random
        
        # Get all valid moves for current player
        valid_moves = []
        for row in range(8):
            for col in range(8):
                piece = board_state.board[row][col]
                if piece and piece.color == board_state.current_player:
                    piece_moves = piece.get_valid_moves(board_state.board)
                    for move_row, move_col in piece_moves:
                        valid_moves.append(((row, col), (move_row, move_col)))
        
        if valid_moves:
            return random.choice(valid_moves)
        
        return None
    
    def get_top_moves(self, board_state, count: int = 3) -> List[Dict[str, Any]]:
        """Return top N random moves (mock implementation)"""
        import random
        
        valid_moves = []
        for row in range(8):
            for col in range(8):
                piece = board_state.board[row][col]
                if piece and piece.color == board_state.current_player:
                    piece_moves = piece.get_valid_moves(board_state.board)
                    for move_row, move_col in piece_moves:
                        valid_moves.append({
                            'move': ((row, col), (move_row, move_col)),
                            'uci': f"{chr(ord('a') + col)}{8 - row}{chr(ord('a') + move_col)}{8 - move_row}",
                            'centipawn': random.randint(-100, 100),
                            'mate': None
                        })
        
        return random.sample(valid_moves, min(count, len(valid_moves)))
    
    def get_evaluation(self, board_state) -> Dict[str, Any]:
        """Return mock evaluation"""
        import random
        
        # Generate mock WDL stats
        wins = random.randint(200, 800)
        draws = random.randint(100, 400) 
        losses = random.randint(200, 800)
        
        return {
            'type': 'cp',
            'value': random.randint(-200, 200),
            'wdl': [wins, draws, losses]
        }
    
    def set_difficulty(self, depth: int) -> None:
        self.depth = depth
    
    def set_skill_level(self, skill: int) -> None:
        self.skill = skill


class ChessEngineManager:
    """Manages different chess engines and provides a unified interface"""
    
    def __init__(self):
        self.engines = {}
        self.active_engine = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize available engines"""
        # Try to initialize Stockfish
        stockfish = StockfishAdapter()
        if stockfish.is_available():
            self.engines['stockfish'] = stockfish
            self.active_engine = stockfish
            print("Stockfish engine available")
        else:
            print("Stockfish not available, using mock engine")
        
        # Always have mock engine as fallback
        self.engines['mock'] = MockEngineAdapter()
        
        # If no other engine is available, use mock
        if not self.active_engine:
            self.active_engine = self.engines['mock']
    
    def get_active_engine(self) -> ChessEngineInterface:
        """Get the currently active engine"""
        return self.active_engine
    
    def set_active_engine(self, engine_name: str) -> bool:
        """Set the active engine by name"""
        if engine_name in self.engines:
            self.active_engine = self.engines[engine_name]
            return True
        return False
    
    def get_available_engines(self) -> List[str]:
        """Get list of available engine names"""
        return list(self.engines.keys())
    
    def is_engine_available(self, engine_name: str) -> bool:
        """Check if a specific engine is available"""
        return engine_name in self.engines and self.engines[engine_name].is_available()