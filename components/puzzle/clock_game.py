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
        self.game_cleared = False
        self.show_done_overlay = False
        self.clear_timer = 0
        self.device = "Computer"
        
        # --- THE SELF-HEALING LOADER ---
        # 1. Get common paths
        script_dir = os.path.dirname(os.path.abspath(__file__))
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # 2. List of everywhere the image might be hiding
        search_locations = [
            os.path.join(script_dir, 'clock.png'),
            os.path.join(script_dir, 'assets', 'clock.png'),
            os.path.join(desktop_path, 'clock.png'),
            os.path.join(downloads_path, 'clock.png')
        ]
        
        self.clock_img = None
        for path in search_locations:
            if os.path.exists(path):
                try:
                    self.clock_img = pygame.image.load(path).convert_alpha()
                    # Scale for grandmother clock verticality
                    self.clock_img = pygame.transform.scale(self.clock_img, (400, 600))
                    self.clock_rect = self.clock_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    print(f"DEBUG: Found and loaded clock at {path}")
                    break
                except:
                    continue

        # --- LOGIC SETTINGS ---
        target_hour = random.randint(1, 12)
        target_min_step = random.choice([0, 15, 30, 45])
        self.target_minutes = (target_hour * 60) + target_min_step
        self.current_minutes = 0.0 
        self.is_dragging = False
        self.tolerance = 8 
        
        # Centered on the white face of your grandfather clock sprite
        self.face_center = (WIDTH // 2, HEIGHT // 2 - 138)
        self.grab_radius = 110 
        self.toggle_rect = pygame.Rect(20, 20, 160, 40)

    def get_angle_from_pos(self, pos):
        dx = pos[0] - self.face_center[0]
        dy = pos[1] - self.face_center[1]
        return (math.degrees(math.atan2(dy, dx)) + 90) % 360

    def handle_input(self, event):
        mx, my = pygame.mouse.get_pos()
        dist = math.hypot(mx - self.face_center[0], my - self.face_center[1])
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.toggle_rect.collidepoint(event.pos):
                self.device = "iPad" if self.device == "Computer" else "Computer"
                self.tolerance = 15 if self.device == "iPad" else 8
                return
            if not self.game_cleared and dist < self.grab_radius:
                self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging:
                if abs(self.current_minutes - self.target_minutes) <= self.tolerance:
                    self.game_cleared = True
                    self.clear_timer = pygame.time.get_ticks()
            self.is_dragging = False

    def update(self):
        if self.is_dragging and not self.game_cleared:
            mx, my = pygame.mouse.get_pos()
            dist = math.hypot(mx - self.face_center[0], my - self.face_center[1])
            if dist > self.grab_radius + 80: # Allow a little extra room for motor slip
                self.is_dragging = False
                return
            new_angle = self.get_angle_from_pos((mx, my))
            target_min_val = (new_angle / 6.0)
            current_hour = int(self.current_minutes // 60)
            self.current_minutes = (current_hour * 60) + target_min_val
            
        if self.game_cleared and not self.show_done_overlay:
            if pygame.time.get_ticks() - self.clear_timer > 800:
                self.show_done_overlay = True

    def draw_pixel_hand(self, length, angle, color, thickness):
        rad = math.radians(angle - 90)
        end_x = self.face_center[0] + math.cos(rad) * length
        end_y = self.face_center[1] + math.sin(rad) * length
        pygame.draw.line(self.screen, color, self.face_center, (int(end_x), int(end_y)), thickness)
        pygame.draw.circle(self.screen, color, self.face_center, thickness // 2 + 2)

    def draw(self):
        self.screen.fill((45, 47, 50)) 
        
        # 1. CLOCK BODY
        if self.clock_img:
            self.screen.blit(self.clock_img, self.clock_rect)
        else:
            # Fallback if the loader fails
            pygame.draw.rect(self.screen, (255, 0, 255), (WIDTH//2-150, HEIGHT//2-250, 300, 500))

        # 2. TARGET TEXT (Original font style)
        font = pygame.font.SysFont(None, 42)
        h = int(self.target_minutes // 60)
        m = int(self.target_minutes % 60)
        time_text = font.render(f"SET TIME: {h:02}:{m:02}", True, (0, 255, 127))
        self.screen.blit(time_text, time_text.get_rect(center=(WIDTH//2, 120)))

        # 3. CLOCK HANDS
        # Hour Hand
        hour_angle = (self.current_minutes / 60.0) * 30
        self.draw_pixel_hand(45, hour_angle, (55, 30, 20), 10)
        # Minute Hand
        minute_angle = (self.current_minutes % 60.0) * 6
        self.draw_pixel_hand(75, minute_angle, (40, 20, 15), 6)

        # 4. UI
        pygame.draw.rect(self.screen, (30, 32, 35), self.toggle_rect, border_radius=10)
        ui_f = pygame.font.SysFont(None, 24)
        mode_text = ui_f.render(f"Mode: {self.device}", True, (255, 255, 255))
        self.screen.blit(mode_text, (self.toggle_rect.x + 15, self.toggle_rect.y + 10))

        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            big_f = pygame.font.SysFont(None, 120)
            done = big_f.render("DONE!", True, (0, 255, 127))
            self.screen.blit(done, done.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Clock Sync Task")
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