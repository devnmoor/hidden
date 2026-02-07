import pygame
import sys
import os
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000 
FPS = 60
MARGIN_1_5_INCH = 144  

class MirrorRoom:
    def __init__(self, screen):
        self.screen = screen
        self.done = False
        self.game_cleared = False
        self.device = "Computer"
        self.brush_size = 25
        
        # --- ROBUST PATH LOADING ---
        # 1. Get the directory where THIS file is saved
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Try to find 'assets' in the current folder OR one folder up
        # This handles moving the code between 'test.py' and 'components/puzzle/mirror_game.py'
        possible_paths = [
            os.path.join(current_dir, 'assets', 'mirror.png'), # If assets is in the same folder
            os.path.join(current_dir, '..', 'assets', 'mirror.png'), # If assets is one folder up
            os.path.join(current_dir, '..', '..', 'assets', 'mirror.png') # If assets is two folders up
        ]
        
        original_img = None
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    original_img = pygame.image.load(path).convert_alpha()
                    print(f"Successfully loaded mirror from: {path}")
                    break
                except:
                    continue

        if original_img:
            w, h = original_img.get_size()
            scale_factor = (HEIGHT * 0.85) / h
            self.mirror_img = pygame.transform.scale(original_img, (int(w * scale_factor), int(HEIGHT * 0.85)))
        else:
            # Fallback if image still can't be found
            print("Warning: Could not find assets/mirror.png. Check folder structure.")
            self.mirror_img = pygame.Surface((400, 850))
            self.mirror_img.fill((180, 180, 180))

        # IMPORTANT: Define self.rect BEFORE calling create_restricted_dirt
        self.rect = self.mirror_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # --- DIRT LAYER ---
        self.dirt_layer = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.create_restricted_dirt()
        self.toggle_rect = pygame.Rect(20, 20, 160, 40)

    def create_restricted_dirt(self):
        self.dirt_layer.fill((0, 0, 0, 0))
        min_x = MARGIN_1_5_INCH
        max_x = self.rect.width - MARGIN_1_5_INCH
        min_y = MARGIN_1_5_INCH
        max_y = self.rect.height - MARGIN_1_5_INCH

        if max_x > min_x and max_y > min_y:
            for _ in range(10):
                x = random.randint(min_x, max_x)
                y = random.randint(min_y, max_y)
                size = random.randint(40, 70)
                for r in range(size, 0, -4):
                    alpha = 240 - (r * 3)
                    if alpha < 0: alpha = 0
                    pygame.draw.circle(self.dirt_layer, (35, 30, 25, alpha), (x, y), r)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.toggle_rect.collidepoint(event.pos):
                self.device = "iPad" if self.device == "Computer" else "Computer"
                self.brush_size = 50 if self.device == "iPad" else 25

    def update(self):
        if self.game_cleared: return
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                lx, ly = mx - self.rect.x, my - self.rect.y
                brush = pygame.Surface((self.brush_size*2, self.brush_size*2), pygame.SRCALPHA)
                pygame.draw.circle(brush, (0,0,0,150), (self.brush_size, self.brush_size), self.brush_size)
                self.dirt_layer.blit(brush, (lx-self.brush_size, ly-self.brush_size), special_flags=pygame.BLEND_RGBA_SUB)
                
                # Zero-pixel tolerance check
                if pygame.mask.from_surface(self.dirt_layer).count() == 0:
                    self.game_cleared = True

    def draw(self):
        self.screen.fill((15, 15, 20))
        self.screen.blit(self.mirror_img, self.rect)
        self.screen.blit(self.dirt_layer, self.rect)
        
        # Toggle UI
        pygame.draw.rect(self.screen, (45, 45, 50), self.toggle_rect, border_radius=10)
        font = pygame.font.SysFont(None, 24)
        mode_text = font.render(f"Mode: {self.device}", True, (255, 255, 255))
        self.screen.blit(mode_text, (self.toggle_rect.x + 15, self.toggle_rect.y + 10))

        if self.game_cleared:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            big_font = pygame.font.SysFont(None, 120)
            done_text = big_font.render("DONE!", True, (0, 255, 127))
            self.screen.blit(done_text, done_text.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    room = MirrorRoom(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            room.handle_input(event)
        room.update()
        room.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
    