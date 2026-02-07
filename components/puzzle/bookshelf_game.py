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
        
        # --- 1. SPRITE LOADING ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Checking local folder and assets folder for bookshelf.png
        paths = [
            os.path.join(script_dir, 'bookshelf.png'),
            os.path.join(script_dir, 'assets', 'bookshelf.png')
        ]
        
        self.bg_img = None
        for path in paths:
            if os.path.exists(path):
                self.bg_img = pygame.image.load(path).convert()
                self.bg_img = pygame.transform.scale(self.bg_img, (WIDTH, HEIGHT))
                break

        # --- 2. GAME STATE ---
        self.book_h = 44 # Matches the chunky pixel art style
        self.stack = [] # Each element: [relative_x, width, color_index]
        self.stack_center_x = WIDTH // 2
        
        # Starting book is automatically at the bottom
        self.base_y = HEIGHT - 110 
        self.stack.append([0, 220, 0]) 
        
        self.falling_book = None
        self.top_shelf_y = 200 # Game ends when books reach this height
        
        # Colors sampled from your bookshelf palette
        self.colors = [
            (115, 62, 57),  # Muted Red
            (165, 105, 63), # Light Brown
            (85, 93, 46),   # Moss Green
            (139, 64, 73),  # Rose
            (60, 45, 35)    # Dark Wood
        ]

    def spawn_book(self):
        w = random.randint(150, 210)
        x = random.randint(50, WIDTH - w - 50)
        color_idx = random.randint(0, len(self.colors)-1)
        speed = 5 + (len(self.stack) * 0.4) 
        self.falling_book = [x, -50, w, color_idx, speed]

    def update(self):
        if self.game_cleared:
            if pygame.time.get_ticks() - self.clear_timer > 1000:
                self.show_done_overlay = True
            return

        # Move the entire stack horizontally with mouse
        mx, _ = pygame.mouse.get_pos()
        self.stack_center_x = mx

        if not self.falling_book:
            self.spawn_book()
        else:
            self.falling_book[1] += self.falling_book[4] # Drop book
            
            # Find the top of the current stack
            top_y = self.base_y - (len(self.stack)-1) * self.book_h
            
            # Collision detection
            if self.falling_book[1] + self.book_h >= top_y:
                fb_x, fb_y, fb_w, fb_c, _ = self.falling_book
                
                # Get the top book's actual world boundaries
                top_book = self.stack[-1]
                top_left = self.stack_center_x + top_book[0] - (top_book[1] // 2)
                top_right = top_left + top_book[1]
                
                # Check for overlap
                if fb_x < top_right and fb_x + fb_w > top_left:
                    # Successful catch!
                    rel_x = (fb_x + fb_w/2) - self.stack_center_x
                    self.stack.append([rel_x, fb_w, fb_c])
                    self.falling_book = None
                    
                    # End game if we reach the top
                    if top_y - self.book_h <= self.top_shelf_y:
                        self.game_cleared = True
                        self.clear_timer = pygame.time.get_ticks()
                else:
                    # Reset game if you miss
                    if self.falling_book[1] > HEIGHT:
                        self.__init__(self.screen)

    def draw_book(self, x, y, w, color_idx):
        color = self.colors[color_idx]
        # Main Spine
        pygame.draw.rect(self.screen, color, (x, y, w, self.book_h))
        # Top highlight (for 3D look)
        pygame.draw.rect(self.screen, (255, 255, 255, 40), (x, y, w, 6))
        # Pages (White side)
        pygame.draw.rect(self.screen, (245, 240, 225), (x + 10, y + 6, w - 20, self.book_h - 12))
        # Spine shadow
        pygame.draw.rect(self.screen, (0, 0, 0, 60), (x, y, 12, self.book_h))

    def draw(self):
        # 1. Draw Background
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill((50, 40, 35))

        # 2. Draw the Stack
        for i, book in enumerate(self.stack):
            bx = self.stack_center_x + book[0] - (book[1] // 2)
            by = self.base_y - (i * self.book_h)
            self.draw_book(bx, by, book[1], book[2])

        # 3. Draw Falling Book
        if self.falling_book:
            fb = self.falling_book
            self.draw_book(fb[0], fb[1], fb[2], fb[3])

        # 4. Victory Screen
        if self.show_done_overlay:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            font = pygame.font.SysFont("Arial", 100, bold=True)
            text = font.render("ORGANIZED!", True, (150, 255, 100))
            self.screen.blit(text, text.get_rect(center=(WIDTH//2, HEIGHT//2)))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = BookCatcher(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        game.update(); game.draw()
        pygame.display.flip(); clock.tick(FPS)

if __name__ == "__main__":
    main()