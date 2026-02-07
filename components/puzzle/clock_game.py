import pygame
import sys
import os
import math
import random

# --- PATH RESOLUTION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
IMAGE_PATH = os.path.join(ROOT_DIR, "assets", "clock1.png")

WIDTH, HEIGHT = 800, 1000
FPS = 60

class ClockGame:
    def __init__(self, screen):
        self.screen = screen
        self.game_cleared = False
        self.show_done_overlay = False
        self.clear_timer = 0
        
        self.target_hour = random.randint(1, 12)
        self.target_minute = random.randint(0, 59)
        
        self.current_hour = 0
        self.current_minute = 0
        
        self.active_hand = None
        self.is_dragging = False

        self.bg_img = None
        if os.path.exists(IMAGE_PATH):
            try:
                original = pygame.image.load(IMAGE_PATH).convert_alpha()
                orig_w, orig_h = original.get_size()
                new_w = 700
                aspect_ratio = orig_h / orig_w
                new_h = int(new_w * aspect_ratio)
                self.bg_img = pygame.transform.scale(original, (new_w, new_h))
                self.img_rect = self.bg_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
                
                face_y_offset = int(new_h * 0.65)
                self.center = (self.img_rect.centerx + 5, self.img_rect.top + face_y_offset)
                self.radius = 145 
            except Exception as e:
                print(f"Error: {e}")
        
        if not self.bg_img:
            self.center = (WIDTH // 2, HEIGHT // 2)
            self.radius = 180

    def get_angle_from_mouse(self, mouse_pos):
        dx = mouse_pos[0] - self.center[0]
        dy = mouse_pos[1] - self.center[1]
        return (math.degrees(math.atan2(dy, dx)) + 90) % 360

    def draw_hand(self, val, is_hour, length_mult, color, thickness, alpha=255):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        angle_deg = (val % 12 * 30) if is_hour else (val * 6)
        angle = math.radians(angle_deg - 90)
        
        end_x = self.center[0] + (self.radius * length_mult) * math.cos(angle)
        end_y = self.center[1] + (self.radius * length_mult) * math.sin(angle)
        pygame.draw.line(surf, (*color, alpha), self.center, (end_x, end_y), thickness)
        self.screen.blit(surf, (0, 0))

    def check_win(self):
        m_diff = abs(self.current_minute - self.target_minute)
        if m_diff > 30: m_diff = 60 - m_diff
        
        # We check hour hand based on the 12-hour cycle
        h_target_pos = self.target_hour + (self.target_minute / 60)
        h_diff = abs((self.current_hour % 12) - (h_target_pos % 12))
        if h_diff > 6: h_diff = 12 - h_diff

        if m_diff <= 4.0 and h_diff <= 0.8:
            self.current_minute = self.target_minute
            self.current_hour = h_target_pos
            self.game_cleared = True
            self.clear_timer = pygame.time.get_ticks()

    def draw(self):
        self.screen.fill((28, 24, 22)) 
        if self.bg_img:
            self.screen.blit(self.bg_img, self.img_rect)
        
        font = pygame.font.SysFont("Arial", 80, bold=True)
        goal_txt = font.render(f"SET: {self.target_hour}:{self.target_minute:02d}", True, (255, 255, 255))
        self.screen.blit(goal_txt, goal_txt.get_rect(center=(WIDTH//2, 100)))

        # Shadows
        self.draw_hand(self.target_minute, False, 0.75, (200, 0, 0), 12, 50) 
        self.draw_hand(self.target_hour + (self.target_minute / 60), True, 0.45, (0, 0, 0), 16, 50)          

        # Player Hands
        self.draw_hand(self.current_minute, False, 0.8, (220, 30, 30), 8) 
        self.draw_hand(self.current_hour, True, 0.5, (20, 20, 20), 12)    
        
        pygame.draw.circle(self.screen, (10, 10, 10), self.center, 8)

        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 230))
            self.screen.blit(overlay, (0, 0))
            done_txt = font.render("DONE!", True, (0, 255, 150))
            self.screen.blit(done_txt, done_txt.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = ClockGame(screen)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
            
            if not game.game_cleared:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dist = math.hypot(mouse_pos[0]-game.center[0], mouse_pos[1]-game.center[1])
                    # Only start dragging if clicking inside the clock radius
                    if dist < game.radius:
                        game.is_dragging = True
                        game.active_hand = 'hour' if dist < game.radius * 0.4 else 'minute'

                if event.type == pygame.MOUSEBUTTONUP:
                    if game.is_dragging:
                        game.is_dragging = False
                        game.active_hand = None 
                        game.check_win()

                if event.type == pygame.MOUSEMOTION and game.is_dragging:
                    # ONLY update values if dragging is active
                    angle = game.get_angle_from_mouse(mouse_pos)
                    if game.active_hand == 'minute': 
                        game.current_minute = (angle / 360) * 60
                    elif game.active_hand == 'hour': 
                        game.current_hour = (angle / 360) * 12

        if game.game_cleared and not game.show_done_overlay:
            if pygame.time.get_ticks() - game.clear_timer > 200:
                game.show_done_overlay = True

        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()