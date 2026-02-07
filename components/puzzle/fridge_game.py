import pygame
import sys
import os
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000 
FPS = 60

# Vibrant electrical colors
COLORS = {
    "red": (255, 50, 50),
    "blue": (50, 120, 255),
    "yellow": (255, 210, 0),
    "pink": (255, 80, 200)
}

class WireGame:
    def __init__(self, screen):
        self.screen = screen
        self.done = False
        self.game_cleared = False
        self.device = "Computer"
        self.node_radius = 25 
        
        # --- COORDINATES ---
        self.left_x = 180
        self.right_x = WIDTH - 180
        self.y_positions = [280, 430, 580, 730]
        
        # --- GAME STATE ---
        self.colors_keys = list(COLORS.keys())
        self.left_colors = random.sample(self.colors_keys, len(self.colors_keys))
        self.right_colors = random.sample(self.colors_keys, len(self.colors_keys))
        
        self.active_line = None
        self.completed_connections = []
        
        self.toggle_rect = pygame.Rect(20, 20, 160, 40)

    def draw_beveled_wire(self, start, end, color):
        """Draws a wire with a shadow/highlight to look 3D."""
        shadow_color = (max(0, color[0]-80), max(0, color[1]-80), max(0, color[2]-80))
        # Draw the shadow (slightly offset and thicker)
        pygame.draw.line(self.screen, shadow_color, (start[0], start[1]+4), (end[0], end[1]+4), 16)
        # Draw the main wire
        pygame.draw.line(self.screen, color, start, end, 12)
        # Draw a slight highlight on top
        highlight = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50))
        pygame.draw.line(self.screen, highlight, (start[0], start[1]-2), (end[0], end[1]-2), 4)

    def handle_input(self, event):
        mx, my = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.toggle_rect.collidepoint(event.pos):
                self.device = "iPad" if self.device == "Computer" else "Computer"
                self.node_radius = 48 if self.device == "iPad" else 25
                return

            for i, y in enumerate(self.y_positions):
                if not any(conn[0] == i for conn in self.completed_connections):
                    dist = ((mx - self.left_x)**2 + (my - y)**2)**0.5
                    if dist < self.node_radius:
                        self.active_line = i
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.active_line is not None:
                for i, y in enumerate(self.y_positions):
                    dist = ((mx - self.right_x)**2 + (my - y)**2)**0.5
                    if dist < self.node_radius:
                        if self.left_colors[self.active_line] == self.right_colors[i]:
                            self.completed_connections.append((self.active_line, i, self.left_colors[self.active_line]))
                self.active_line = None
                if len(self.completed_connections) == len(self.colors_keys):
                    self.game_cleared = True

    def draw(self):
        # Slightly Lighter Gray background
        self.screen.fill((50, 50, 55))
        
        # Draw "Panel Screws" for detail
        for corner in [(40, 120), (WIDTH-40, 120), (40, 880), (WIDTH-40, 880)]:
            pygame.draw.circle(self.screen, (30, 30, 35), corner, 8)

        # Draw Right Sockets
        for i, y in enumerate(self.y_positions):
            color = COLORS[self.right_colors[i]]
            pygame.draw.rect(self.screen, (30, 30, 35), (self.right_x - 10, y - 30, 60, 60), border_radius=5)
            # Terminal Node
            pygame.draw.circle(self.screen, color, (self.right_x + 20, y), 18)

        # Draw Static Connections
        for s_idx, e_idx, color_name in self.completed_connections:
            self.draw_beveled_wire((self.left_x, self.y_positions[s_idx]), 
                                   (self.right_x + 20, self.y_positions[e_idx]), 
                                   COLORS[color_name])

        # Draw Active Dragging Wire
        if self.active_line is not None:
            self.draw_beveled_wire((self.left_x, self.y_positions[self.active_line]), 
                                   pygame.mouse.get_pos(), 
                                   COLORS[self.left_colors[self.active_line]])

        # Draw Left Sockets
        for i, y in enumerate(self.y_positions):
            color = COLORS[self.left_colors[i]]
            pygame.draw.rect(self.screen, (30, 30, 35), (self.left_x - 50, y - 30, 60, 60), border_radius=5)
            # Terminal Node
            pygame.draw.circle(self.screen, color, (self.left_x - 20, y), 18)

        # Toggle UI
        pygame.draw.rect(self.screen, (40, 40, 45), self.toggle_rect, border_radius=10)
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
    pygame.display.set_caption("Fridge Rewiring")
    clock = pygame.time.Clock()
    game = WireGame(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            game.handle_input(event)
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()