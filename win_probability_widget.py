"""
Win Probability Widget
Visual representation of win probabilities with animated bars and colors
"""

import pygame
import math
from typing import List, Tuple


class WinProbabilityWidget:
    """Animated widget showing win probabilities"""
    
    def __init__(self):
        self.current_probs = [33.3, 33.3, 33.3]  # [white_win, draw, black_win]
        self.target_probs = [33.3, 33.3, 33.3]
        self.animation_speed = 0.1
        self.last_update_time = 0
        
    def update_probabilities(self, wdl_stats: List[int]):
        """Update target probabilities from WDL stats"""
        if len(wdl_stats) != 3:
            return
        
        wins, draws, losses = wdl_stats
        total = wins + draws + losses
        
        if total == 0:
            return
        
        # Calculate percentages
        self.target_probs = [
            (wins / total) * 100,
            (draws / total) * 100,
            (losses / total) * 100
        ]
    
    def update_animation(self):
        """Update animation towards target probabilities"""
        for i in range(3):
            diff = self.target_probs[i] - self.current_probs[i]
            if abs(diff) > 0.1:
                self.current_probs[i] += diff * self.animation_speed
            else:
                self.current_probs[i] = self.target_probs[i]
    
    def draw_circular_probability(self, screen, center_x: int, center_y: int, radius: int):
        """Draw circular probability chart"""
        # Background circle
        pygame.draw.circle(screen, (40, 40, 40), (center_x, center_y), radius, 2)
        
        # Calculate angles for each segment
        white_angle = (self.current_probs[0] / 100) * 360
        draw_angle = (self.current_probs[1] / 100) * 360
        black_angle = (self.current_probs[2] / 100) * 360
        
        # Draw segments
        start_angle = -90  # Start from top
        
        # White segment
        if white_angle > 0:
            self._draw_arc_segment(screen, center_x, center_y, radius - 5, 
                                 start_angle, white_angle, (220, 220, 220))
            start_angle += white_angle
        
        # Draw segment  
        if draw_angle > 0:
            self._draw_arc_segment(screen, center_x, center_y, radius - 5,
                                 start_angle, draw_angle, (200, 200, 0))
            start_angle += draw_angle
        
        # Black segment
        if black_angle > 0:
            self._draw_arc_segment(screen, center_x, center_y, radius - 5,
                                 start_angle, black_angle, (80, 80, 80))
        
        # Center text
        font = pygame.font.Font(None, 24)
        prob_text = f"{self.current_probs[0]:.1f}%"
        text_surface = font.render(prob_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(center_x, center_y - 10))
        screen.blit(text_surface, text_rect)
        
        white_text = font.render("Blancas", True, (200, 200, 200))
        white_rect = white_text.get_rect(center=(center_x, center_y + 10))
        screen.blit(white_text, white_rect)
    
    def draw_horizontal_bars(self, screen, x: int, y: int, width: int, height: int):
        """Draw horizontal probability bars"""
        font = pygame.font.Font(None, 20)
        
        # Colors for each outcome
        colors = [
            (220, 220, 220),  # White
            (200, 200, 0),    # Draw (yellow)
            (80, 80, 80)      # Black
        ]
        
        labels = ["Blancas", "Empate", "Negras"]
        
        bar_height = height // 4
        spacing = 5
        
        for i, (prob, color, label) in enumerate(zip(self.current_probs, colors, labels)):
            bar_y = y + i * (bar_height + spacing)
            
            # Label
            label_surface = font.render(f"{label}: {prob:.1f}%", True, (220, 220, 220))
            screen.blit(label_surface, (x, bar_y))
            
            # Bar background
            bar_rect = pygame.Rect(x, bar_y + 20, width, bar_height)
            pygame.draw.rect(screen, (40, 40, 40), bar_rect)
            pygame.draw.rect(screen, (100, 100, 100), bar_rect, 1)
            
            # Filled bar
            fill_width = int((prob / 100) * width)
            if fill_width > 0:
                fill_rect = pygame.Rect(x, bar_y + 20, fill_width, bar_height)
                pygame.draw.rect(screen, color, fill_rect)
                
                # Add glow effect
                glow_rect = pygame.Rect(x, bar_y + 20, fill_width, bar_height)
                pygame.draw.rect(screen, self._lighten_color(color, 0.3), glow_rect, 2)
    
    def draw_evaluation_bar(self, screen, x: int, y: int, width: int, height: int, 
                          evaluation: float):
        """Draw evaluation bar (-10 to +10 scale)"""
        font = pygame.font.Font(None, 20)
        
        # Clamp evaluation to reasonable range
        eval_clamped = max(-10, min(10, evaluation))
        
        # Background
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)
        
        # Center line
        center_x = x + width // 2
        pygame.draw.line(screen, (100, 100, 100), 
                        (center_x, y), (center_x, y + height), 1)
        
        # Evaluation bar
        if eval_clamped > 0:
            # White advantage
            bar_width = int((eval_clamped / 10) * (width // 2))
            bar_rect = pygame.Rect(center_x, y + 2, bar_width, height - 4)
            pygame.draw.rect(screen, (220, 220, 220), bar_rect)
        elif eval_clamped < 0:
            # Black advantage  
            bar_width = int((abs(eval_clamped) / 10) * (width // 2))
            bar_rect = pygame.Rect(center_x - bar_width, y + 2, bar_width, height - 4)
            pygame.draw.rect(screen, (80, 80, 80), bar_rect)
        
        # Evaluation text
        eval_text = f"Eval: {evaluation:+.2f}"
        text_surface = font.render(eval_text, True, (220, 220, 220))
        screen.blit(text_surface, (x, y + height + 5))
    
    def _draw_arc_segment(self, screen, center_x: int, center_y: int, radius: int,
                         start_angle: float, arc_angle: float, color: Tuple[int, int, int]):
        """Draw an arc segment for pie chart"""
        if arc_angle <= 0:
            return
        
        # Convert to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(start_angle + arc_angle)
        
        # Create points for polygon
        points = [(center_x, center_y)]
        
        # Add arc points
        steps = max(3, int(arc_angle / 5))  # More steps for smoother arcs
        for i in range(steps + 1):
            angle = start_rad + (end_rad - start_rad) * (i / steps)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))
        
        # Draw filled polygon
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, self._lighten_color(color, 0.2), points, 2)
    
    def _lighten_color(self, color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Lighten a color by a factor"""
        return tuple(min(255, int(c + (255 - c) * factor)) for c in color)