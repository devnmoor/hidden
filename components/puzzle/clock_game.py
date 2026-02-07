import pygame
import sys
import os
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000
FPS = 60

class ClockGame:
    def __init__(self, screen):
        self.screen = screen
        # Center of the clock face on the sprite
        self.center = (WIDTH // 2, 400) 
        self.radius = 280
        self.game_cleared = False
        self.show_done_overlay = False
        self.clear_timer = 0
        
        # --- 1. TARGET TIME ---
        self.target_hour = random.randint(1, 12)
        self.target_minute = random.choice([0, 15, 30, 45])
        
        # --- 2. PLAYER TIME ---
        self.current_minute = random.randint(0, 59) 
        self.is_dragging = False

        # --- 3. ASSET LOADING ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(script_dir, 'clock1.png')
        
        self.bg_top = None
        if os.path.exists(bg_path):
            full_img = pygame.image.load(bg_path).convert_alpha()
            full_img = pygame.transform.scale(full_img, (WIDTH, HEIGHT))
            # Crop to the top portion where the clock face is
            self.bg_top = full_img.subsurface(pygame.Rect(0, 0, WIDTH, 700))

    def get_angle_from_mouse(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        angle = math.degrees(math.atan2(dy, dx)) + 90
        return angle % 360

    def handle_input(self, event):
        if self.game_cleared: return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            dist = math.hypot(mx - self.center[0], my - self.center[1])
            if dist < self.radius:
                self.is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
            # Check for alignment with the shadow
            if abs(self.current_minute - self.target_minute) <= 4:
                self.current_minute = self.target_minute # Snap to perfect
                self.game_cleared = True
                self.clear_timer = pygame.time.get_ticks()

        if event.type == pygame.MOUSEMOTION and self.is_dragging:
            angle = self.get_angle_from_mouse(event.pos)
            self.current_minute = (angle / 360) * 60

    def draw_hand(self, minutes, hours, length_mult, color, thickness, alpha=255):
        """Helper to draw a clock hand at a specific time."""
        # Create a surface for transparency if alpha < 255
        hand_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        # Calculate angle
        if minutes is not None: # Minute hand
            angle_deg = (minutes / 60) * 360 - 90
        else: # Hour hand
            angle_deg = (hours % 12) * 30 + (self.target_minute * 0.5) - 90
            
        angle_rad = math.radians(angle_deg)
        end_pos = (self.center[0] + (self.radius * length_mult) * math.cos(angle_rad),
                   self.center[1] + (self.radius * length_mult) * math.sin(angle_rad))
        
        # Draw the hand with the specified alpha
        draw_color = (*color, alpha)
        pygame.draw.line(hand_surf, draw_color, self.center, end_pos, thickness)
        self.screen.blit(hand_surf, (0, 0))

    def draw(self):
        self.screen.fill((30, 28, 25))
        
        if self.bg_top:
            self.screen.blit(self.bg_top, (0, 0))

        # 1. DRAW THE SHADOW (Target Position)
        # Target Minute Shadow (Faint Red)
        self.draw_hand(self.target_minute, None, 0.85, (180, 50, 50), 12, alpha=80)
        # Target Hour Shadow (Faint Black)
        self.draw_hand(None, self.target_hour, 0.55, (20, 20, 20), 18, alpha=80)

        # 2. DRAW THE PLAYER HAND (Active Hand)
        # The user only moves the minute hand in this version
        self.draw_hand(self.current_minute, None, 0.85, (220, 40, 40), 8)
        
        # Fixed Hour Hand (Solid Black - matching the target)
        self.draw_hand(None, self.target_hour, 0.55, (20, 20, 20), 14)

        # Center Pin
        pygame.draw.circle(self.screen, (10, 10, 10), self.center, 12)

        # UI Text
        font = pygame.font.SysFont("Courier", 40, bold=True)
        instr = font.render("MATCH THE SHADOW", True, (200, 200, 200))
        self.screen.blit(instr, instr.get_rect(center=(WIDTH//2, 850)))

        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            done_font = pygame.font.SysFont("Arial", 150, bold=True)
            done_txt = done_font.render("DONE!", True, (100, 255, 100))
            self.screen.blit(done_txt, done_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

    def update(self):
        if self.game_cleared and not self.show_done_overlay:
            if pygame.time.get_ticks() - self.clear_timer > 600:
                self.show_done_overlay = True

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = ClockGame(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            game.handle_input(event)
        game.update(); game.draw()
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    main()