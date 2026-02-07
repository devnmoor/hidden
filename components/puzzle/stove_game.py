import pygame
import sys
import os
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000 
FPS = 60
PIXEL_SIZE = 4 

class StoveGame:
    def __init__(self, screen):
        self.screen = screen
        self.game_cleared = False
        self.show_done_overlay = False
        self.clear_timer = 0
        self.device = "Computer"
        
        # --- 1. SPRITE LOADING ---
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_path, 'assets', 'stove_burner.png')
        
        try:
            raw_img = pygame.image.load(img_path).convert_alpha()
            self.stove_img = pygame.transform.scale(raw_img, (450, 450))
            self.stove_rect = self.stove_img.get_rect(center=(WIDTH // 2, 320))
        except:
            print("Sprite 'stove_burner.png' not found. Using pixel fallback.")
            self.stove_img = None

        # --- 2. LOGIC ---
        self.target_angle = random.randint(110, 310)
        self.current_angle = 0
        self.is_dragging = False
        self.tolerance = 5 
        self.path_width = 45 
        
        # --- 3. POSITIONING ---
        self.center = (WIDTH // 2, HEIGHT // 2 + 150)
        self.knob_radius = 100
        self.toggle_rect = pygame.Rect(20, 20, 160, 40)

    def draw_pixel_circle(self, center, radius, color, width=0):
        for x in range(-radius, radius + PIXEL_SIZE, PIXEL_SIZE):
            for y in range(-radius, radius + PIXEL_SIZE, PIXEL_SIZE):
                dist = math.sqrt(x*x + y*y)
                if width == 0: 
                    if dist <= radius:
                        pygame.draw.rect(self.screen, color, (center[0] + x, center[1] + y, PIXEL_SIZE, PIXEL_SIZE))
                else: 
                    if radius - width <= dist <= radius:
                        pygame.draw.rect(self.screen, color, (center[0] + x, center[1] + y, PIXEL_SIZE, PIXEL_SIZE))

    def get_angle_from_pos(self, pos):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return (math.degrees(math.atan2(dy, dx)) + 90) % 360

    def handle_input(self, event):
        mx, my = pygame.mouse.get_pos()
        dist = math.hypot(mx - self.center[0], my - self.center[1])
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.toggle_rect.collidepoint(event.pos):
                self.device = "iPad" if self.device == "Computer" else "Computer"
                self.path_width = 75 if self.device == "iPad" else 45
                return
            if not self.game_cleared and abs(dist - self.knob_radius) < 35:
                self.is_dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_dragging:
                # Success Check
                if abs(self.current_angle - self.target_angle) <= self.tolerance:
                    self.game_cleared = True
                    self.clear_timer = pygame.time.get_ticks() # Start the delay timer
                else:
                    self.current_angle = 0 
            self.is_dragging = False

    def update(self):
        # 1. Handle Knob Rotation
        if self.is_dragging and not self.game_cleared:
            mx, my = pygame.mouse.get_pos()
            dist = math.hypot(mx - self.center[0], my - self.center[1])
            
            # Reset if cursor leaves the circular track
            if abs(dist - self.knob_radius) > self.path_width:
                self.is_dragging = False
                self.current_angle = 0 
                return

            target_angle = self.get_angle_from_pos((mx, my))
            diff = (target_angle - self.current_angle + 180) % 360 - 180
            if abs(diff) < 30: 
                self.current_angle = (self.current_angle + diff * 0.25) % 360

        # 2. Handle the "DONE!" Delay
        if self.game_cleared and not self.show_done_overlay:
            if pygame.time.get_ticks() - self.clear_timer > 800: # 800ms delay
                self.show_done_overlay = True

    def draw(self):
        self.screen.fill((45, 47, 50)) 

        # --- DRAW STOVE ---
        if self.stove_img:
            self.screen.blit(self.stove_img, self.stove_rect)
            
            # Real-time Proximity Glow
            dist_to_target = abs((self.current_angle - self.target_angle + 180) % 360 - 180)
            if dist_to_target < 60 or self.game_cleared:
                glow_surf = pygame.Surface((450, 450), pygame.SRCALPHA)
                
                # Full brightness if won or very close
                if self.game_cleared or dist_to_target <= self.tolerance:
                    max_alpha = 180
                else:
                    max_alpha = int(150 * (1 - (dist_to_target / 60)))

                for r in range(160, 0, -15):
                    ring_alpha = min(max_alpha, (160 - r) + (max_alpha // 2))
                    pygame.draw.circle(glow_surf, (255, 30, 0, ring_alpha), (225, 225), r)
                self.screen.blit(glow_surf, self.stove_rect)
        else:
            # Fallback Pixel Burner
            burner_center = (WIDTH // 2, 320)
            dist_to_target = abs((self.current_angle - self.target_angle + 180) % 360 - 180)
            for r in [160, 120, 80]:
                self.draw_pixel_circle(burner_center, r, (20, 20, 22), width=10)
            
            if self.game_cleared or dist_to_target < 10:
                color = (255, 60, 0)
            elif dist_to_target < 60:
                color = (int(100 * (1 - dist_to_target/60)), 20, 10)
            else:
                color = (35, 35, 40)
            self.draw_pixel_circle(burner_center, 40, color)

        # --- TARGET ---
        t_rad = math.radians(self.target_angle - 90)
        tx = self.center[0] + math.cos(t_rad) * (self.knob_radius + 40)
        ty = self.center[1] + math.sin(t_rad) * (self.knob_radius + 40)
        pygame.draw.rect(self.screen, (0, 255, 100), (int(tx)-8, int(ty)-8, 16, 16))

        # --- KNOB ---
        self.draw_pixel_circle(self.center, self.knob_radius + 6, (15, 15, 18))
        self.draw_pixel_circle(self.center, self.knob_radius, (100, 100, 105))
        self.draw_pixel_circle(self.center, self.knob_radius - 20, (80, 80, 85))
        
        rad = math.radians(self.current_angle - 90)
        px = self.center[0] + math.cos(rad) * (self.knob_radius - 15)
        py = self.center[1] + math.sin(rad) * (self.knob_radius - 15)
        pygame.draw.rect(self.screen, (220, 30, 30), (int(px)-10, int(py)-10, 20, 20))

        # --- UI ---
        pygame.draw.rect(self.screen, (30, 32, 35), self.toggle_rect, border_radius=10)
        font = pygame.font.SysFont(None, 24)
        mode_text = font.render(f"Mode: {self.device}", True, (255, 255, 255))
        self.screen.blit(mode_text, (self.toggle_rect.x + 15, self.toggle_rect.y + 10))

        # --- DELAYED OVERLAY ---
        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            big_font = pygame.font.SysFont(None, 120)
            done_text = big_font.render("DONE!", True, (0, 255, 127))
            self.screen.blit(done_text, done_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stove Calibration Lab")
    clock = pygame.time.Clock()
    game = StoveGame(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            game.handle_input(event)
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()