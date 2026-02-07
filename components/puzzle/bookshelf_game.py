import pygame
import sys
import os
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000
FPS = 60

class BookCatcher:
    def __init__(self, screen):
        self.screen = screen
        self.game_cleared = False
        self.show_done_overlay = False
        self.clear_timer = 0
        
        # --- 1. THE LOADER ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        search_paths = [
            os.path.join(script_dir, 'bookshelf.png'),
            os.path.join(os.path.expanduser("~"), "Downloads", "bookshelf.png"),
            os.path.join(os.path.expanduser("~"), "Desktop", "bookshelf.png")
        ]
        
        self.bg_img = None
        for path in search_paths:
            if os.path.exists(path):
                try:
                    loaded = pygame.image.load(path).convert()
                    self.bg_img = pygame.transform.scale(loaded, (WIDTH, HEIGHT))
                    break
                except: continue

        # --- 2. GAME STATE ---
        self.book_h = 48 
        self.stack = [] 
        self.stack_center_x = WIDTH // 2
        
        # RAISED BASELINE: Moved up to 250 pixels from bottom so it's clearly visible
        self.base_y = HEIGHT - 250 
        
        # Start with the foundation book pre-placed
        # [relative_x, width, color_index]
        self.stack.append([0, 240, 0]) 
        
        self.falling_book = None
        self.top_shelf_y = 150 # Height to reach for victory
        
        # Pixel Art Palette
        self.colors = [
            (145, 70, 60), (175, 120, 75), (95, 105, 55), (110, 55, 80), (70, 50, 40)
        ]

    def spawn_book(self):
        w = random.randint(160, 240)
        x = random.randint(50, WIDTH - w - 50)
        color_idx = random.randint(0, len(self.colors)-1)
        speed = 5 + (len(self.stack) * 0.2) 
        self.falling_book = {'x': x, 'y': -80, 'w': w, 'c': color_idx, 's': speed}

    def update(self):
        if self.game_cleared:
            if pygame.time.get_ticks() - self.clear_timer > 800:
                self.show_done_overlay = True
            return

        mx, _ = pygame.mouse.get_pos()
        self.stack_center_x = mx

        if not self.falling_book:
            self.spawn_book()
        else:
            self.falling_book['y'] += self.falling_book['s']
            
            # Find the top of the stack
            top_y = self.base_y - (len(self.stack)-1) * self.book_h
            
            # Catch Logic (Increased collision window for smoother feel)
            if self.falling_book['y'] + self.book_h >= top_y and self.falling_book['y'] < top_y + 30:
                fb = self.falling_book
                top_book = self.stack[-1]
                
                top_abs_left = self.stack_center_x + top_book[0] - (top_book[1] // 2)
                top_abs_right = top_abs_left + top_book[1]
                
                if fb['x'] < top_abs_right and fb['x'] + fb['w'] > top_abs_left:
                    rel_x = (fb['x'] + fb['w']/2) - self.stack_center_x
                    self.stack.append([rel_x, fb['w'], fb['c']])
                    self.falling_book = None 
                    
                    if top_y - self.book_h <= self.top_shelf_y:
                        self.game_cleared = True
                        self.clear_timer = pygame.time.get_ticks()

            if self.falling_book and self.falling_book['y'] > HEIGHT:
                self.falling_book = None 

    def draw_pixel_book(self, x, y, w, color_idx):
        color = self.colors[color_idx]
        dark = (max(0, color[0]-40), max(0, color[1]-40), max(0, color[2]-40))
        light = (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30))
        
        pygame.draw.rect(self.screen, (25, 20, 15), (x, y, w, self.book_h)) # Outline
        pygame.draw.rect(self.screen, color, (x + 4, y + 4, w - 8, self.book_h - 8)) # Main
        pygame.draw.rect(self.screen, light, (x + 4, y + 4, w - 8, 4)) # Top shine
        pygame.draw.rect(self.screen, (245, 240, 220), (x + w - 45, y + 8, 35, self.book_h - 16)) # Pages
        pygame.draw.rect(self.screen, dark, (x + 4, y + 4, 15, self.book_h - 8)) # Spine

    def draw(self):
        # 1. Background
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((40, 30, 25))

        # 2. Draw Shelf Platform (Visual guide for the floor)
        pygame.draw.rect(self.screen, (60, 40, 30), (0, self.base_y + self.book_h, WIDTH, 20))
        pygame.draw.rect(self.screen, (20, 10, 5), (0, self.base_y + self.book_h, WIDTH, 20), 4)

        # 3. Draw Stack
        for i, book in enumerate(self.stack):
            bx = self.stack_center_x + book[0] - (book[1] // 2)
            by = self.base_y - (i * self.book_h)
            self.draw_pixel_book(bx, by, book[1], book[2])

        # 4. Draw Falling Book
        if self.falling_book:
            fb = self.falling_book
            self.draw_pixel_book(fb['x'], fb['y'], fb['w'], fb['c'])

        # 5. Victory Overlay
        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            font = pygame.font.SysFont("Arial", 120, bold=True)
            text = font.render("DONE!", True, (100, 255, 100))
            self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Library Task")
    clock = pygame.time.Clock()
    game = BookCatcher(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        game.update(); game.draw()
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    main()