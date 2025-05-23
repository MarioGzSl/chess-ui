"""
Chess Analysis Module
Provides analysis features using chess engines
"""

import pygame
from typing import List, Dict, Any, Optional
from chess_engine_adapter import ChessEngineManager


class ChessAnalysisPanel:
    """Panel that shows engine analysis"""
    
    def __init__(self, engine_manager: ChessEngineManager):
        self.engine_manager = engine_manager
        self.show_analysis = False
        self.current_evaluation = {}
        self.top_moves = []
        self.analysis_depth = 10
    
    def toggle_analysis(self):
        """Toggle analysis display"""
        self.show_analysis = not self.show_analysis
    
    def update_analysis(self, board_state):
        """Update analysis for current position"""
        if not self.show_analysis:
            return
        
        engine = self.engine_manager.get_active_engine()
        if engine and engine.is_available():
            self.current_evaluation = engine.get_evaluation(board_state)
            self.top_moves = engine.get_top_moves(board_state, 5)
    
    def draw_analysis(self, screen, panel_x, start_y, panel_width):
        """Draw analysis information"""
        if not self.show_analysis:
            return start_y
        
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        color = (220, 220, 220)
        
        y_pos = start_y
        
        # Analysis title
        title = font.render("Engine Analysis", True, color)
        screen.blit(title, (panel_x + 10, y_pos))
        y_pos += 30
        
        # Current evaluation
        if self.current_evaluation:
            eval_text = self._format_evaluation(self.current_evaluation)
            eval_surface = small_font.render(f"Evaluation: {eval_text}", True, color)
            screen.blit(eval_surface, (panel_x + 10, y_pos))
            y_pos += 25
            
            # Win probability (WDL stats)
            if 'wdl' in self.current_evaluation:
                y_pos = self._draw_win_probability(screen, panel_x, y_pos, panel_width, 
                                                  self.current_evaluation['wdl'], small_font)
        
        # Top moves
        if self.top_moves:
            moves_title = small_font.render("Best moves:", True, color)
            screen.blit(moves_title, (panel_x + 10, y_pos))
            y_pos += 20
            
            for i, move_data in enumerate(self.top_moves[:3]):
                move_text = self._format_move(move_data, i + 1)
                move_surface = small_font.render(move_text, True, color)
                screen.blit(move_surface, (panel_x + 15, y_pos))
                y_pos += 18
        
        return y_pos + 10
    
    def _format_evaluation(self, evaluation: Dict[str, Any]) -> str:
        """Format evaluation for display"""
        if 'type' in evaluation:
            if evaluation['type'] == 'cp':
                # Centipawn evaluation
                cp = evaluation.get('value', 0)
                return f"{cp/100:.2f}"
            elif evaluation['type'] == 'mate':
                # Mate in N moves
                mate = evaluation.get('value', 0)
                return f"Mate in {abs(mate)}"
        
        return "0.00"
    
    def _format_move(self, move_data: Dict[str, Any], rank: int) -> str:
        """Format move for display"""
        uci = move_data.get('uci', '')
        
        if move_data.get('mate') is not None:
            eval_str = f"M{abs(move_data['mate'])}"
        elif move_data.get('centipawn') is not None:
            cp = move_data['centipawn']
            eval_str = f"{cp/100:+.2f}"
        else:
            eval_str = "0.00"
        
        return f"{rank}. {uci} ({eval_str})"
    
    def _format_win_probability(self, wdl_stats: List[int]) -> List[str]:
        """Format WDL (Win/Draw/Loss) statistics for display"""
        if len(wdl_stats) != 3:
            return ["Probabilities: N/A"]
        
        wins, draws, losses = wdl_stats
        total = wins + draws + losses
        
        if total == 0:
            return ["Probabilities: N/A"]
        
        # Calculate percentages
        win_pct = (wins / total) * 100
        draw_pct = (draws / total) * 100
        loss_pct = (losses / total) * 100
        
        return [
            f"Probabilities:",
            f"  White: {win_pct:.1f}%",
            f"  Draw:  {draw_pct:.1f}%", 
            f"  Black:  {loss_pct:.1f}%"
        ]
    
    def _draw_win_probability(self, screen, panel_x: int, start_y: int, 
                            panel_width: int, wdl_stats: List[int], font) -> int:
        """Draw win probability with visual bars"""
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
        bar_width = panel_width - 40
        bar_height = 12
        
        # Title
        title = font.render("Win probabilities:", True, (220, 220, 220))
        screen.blit(title, (panel_x + 10, y_pos))
        y_pos += 25
        
        # White wins bar
        white_text = font.render(f"White: {win_pct:.1f}%", True, (220, 220, 220))
        screen.blit(white_text, (panel_x + 10, y_pos))
        y_pos += 18
        
        # White bar
        white_bar_width = int((win_pct / 100) * bar_width)
        white_rect = pygame.Rect(panel_x + 10, y_pos, white_bar_width, bar_height)
        pygame.draw.rect(screen, (200, 200, 200), white_rect)  # Light gray for white
        pygame.draw.rect(screen, (100, 100, 100), 
                        pygame.Rect(panel_x + 10, y_pos, bar_width, bar_height), 1)
        y_pos += 18
        
        # Draw bar
        draw_text = font.render(f"Draw: {draw_pct:.1f}%", True, (220, 220, 220))
        screen.blit(draw_text, (panel_x + 10, y_pos))
        y_pos += 18
        
        # Draw bar
        draw_bar_width = int((draw_pct / 100) * bar_width)
        draw_rect = pygame.Rect(panel_x + 10, y_pos, draw_bar_width, bar_height)
        pygame.draw.rect(screen, (150, 150, 0), draw_rect)  # Yellow for draw
        pygame.draw.rect(screen, (100, 100, 100), 
                        pygame.Rect(panel_x + 10, y_pos, bar_width, bar_height), 1)
        y_pos += 18
        
        # Black wins bar
        black_text = font.render(f"Black: {loss_pct:.1f}%", True, (220, 220, 220))
        screen.blit(black_text, (panel_x + 10, y_pos))
        y_pos += 18
        
        # Black bar
        black_bar_width = int((loss_pct / 100) * bar_width)
        black_rect = pygame.Rect(panel_x + 10, y_pos, black_bar_width, bar_height)
        pygame.draw.rect(screen, (80, 80, 80), black_rect)  # Dark gray for black
        pygame.draw.rect(screen, (100, 100, 100), 
                        pygame.Rect(panel_x + 10, y_pos, bar_width, bar_height), 1)
        y_pos += 25
        
        return y_pos


class EngineSettingsPanel:
    """Panel for engine configuration"""
    
    def __init__(self, engine_manager: ChessEngineManager):
        self.engine_manager = engine_manager
        self.show_settings = False
        self.skill_level = 20
        self.depth = 10
    
    def toggle_settings(self):
        """Toggle settings display"""
        self.show_settings = not self.show_settings
    
    def draw_settings(self, screen, panel_x, start_y, panel_width):
        """Draw engine settings"""
        if not self.show_settings:
            return start_y
        
        font = pygame.font.Font(None, 24)
        small_font = pygame.font.Font(None, 20)
        color = (220, 220, 220)
        
        y_pos = start_y
        
        # Settings title
        title = font.render("Engine Configuration", True, color)
        screen.blit(title, (panel_x + 10, y_pos))
        y_pos += 30
        
        # Engine info
        engine = self.engine_manager.get_active_engine()
        if hasattr(engine, 'get_engine_info'):
            info = engine.get_engine_info()
            name_text = small_font.render(f"Engine: {info.get('name', 'Unknown')}", True, color)
            screen.blit(name_text, (panel_x + 10, y_pos))
            y_pos += 20
            
            if 'version' in info:
                version_text = small_font.render(f"Version: {info['version']}", True, color)
                screen.blit(version_text, (panel_x + 10, y_pos))
                y_pos += 20
        
        # Skill level
        skill_text = small_font.render(f"Level: {self.skill_level}/20", True, color)
        screen.blit(skill_text, (panel_x + 10, y_pos))
        y_pos += 20
        
        # Depth
        depth_text = small_font.render(f"Depth: {self.depth}", True, color)
        screen.blit(depth_text, (panel_x + 10, y_pos))
        y_pos += 25
        
        return y_pos + 10
    
    def handle_settings_change(self, setting: str, value: int):
        """Handle settings changes"""
        engine = self.engine_manager.get_active_engine()
        
        if setting == 'skill':
            self.skill_level = max(0, min(20, value))
            if hasattr(engine, 'set_skill_level'):
                engine.set_skill_level(self.skill_level)
        
        elif setting == 'depth':
            self.depth = max(1, min(20, value))
            if hasattr(engine, 'set_difficulty'):
                engine.set_difficulty(self.depth)


class ChessAnalysisManager:
    """Manages all analysis features"""
    
    def __init__(self, engine_manager: ChessEngineManager):
        self.engine_manager = engine_manager
        self.analysis_panel = ChessAnalysisPanel(engine_manager)
        self.settings_panel = EngineSettingsPanel(engine_manager)
        self.auto_analysis = False
    
    def toggle_analysis(self):
        """Toggle analysis display"""
        self.analysis_panel.toggle_analysis()
    
    def toggle_settings(self):
        """Toggle settings display"""
        self.settings_panel.toggle_settings()
    
    def toggle_auto_analysis(self):
        """Toggle automatic analysis"""
        self.auto_analysis = not self.auto_analysis
    
    def update(self, board_state):
        """Update analysis if auto-analysis is enabled"""
        if self.auto_analysis:
            self.analysis_panel.update_analysis(board_state)
    
    def draw(self, screen, panel_x, start_y, panel_width):
        """Draw all analysis components"""
        y_pos = start_y
        
        # Draw analysis panel
        y_pos = self.analysis_panel.draw_analysis(screen, panel_x, y_pos, panel_width)
        
        # Draw settings panel
        y_pos = self.settings_panel.draw_settings(screen, panel_x, y_pos, panel_width)
        
        return y_pos
    
    def get_analysis_buttons(self, panel_x, start_y):
        """Get button definitions for analysis features"""
        button_width = 80
        button_height = 25
        spacing = 5
        
        buttons = []
        
        # Analysis toggle button
        buttons.append({
            'text': 'Analysis',
            'rect': pygame.Rect(panel_x + 10, start_y, button_width, button_height),
            'action': 'toggle_analysis',
            'active': self.analysis_panel.show_analysis
        })
        
        # Settings toggle button
        buttons.append({
            'text': 'Config',
            'rect': pygame.Rect(panel_x + 10 + button_width + spacing, start_y, button_width, button_height),
            'action': 'toggle_settings',
            'active': self.settings_panel.show_settings
        })
        
        return buttons