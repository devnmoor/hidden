import pygame
import sys

# --- CONFIGURATION ---
WIDTH, HEIGHT = 800, 1000
FPS = 60

# --- COLOR PALETTE (Extracted from Clock Sprite) ---
BG_COLOR = (28, 24, 22)        # Dark wood / Deep brown background
ACCENT_COLOR = (180, 140, 100) # Gold / Aged brass from the clock face
TEXT_COLOR = (240, 230, 210)   # Off-white / Parchment for readability
BUTTON_COLOR = (45, 40, 35)    # Lighter wood grain for buttons
HOVER_COLOR = (65, 55, 50)     # Feedback color

# States
START = "start"
INSTRUCTIONS = "instructions"

class HiddenMenu:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("HIDDEN - Escape Room")
        self.clock = pygame.time.Clock()
        self.state = START
        
        # Fonts
        self.title_font = pygame.font.SysFont("Georgia", 90, bold=True)
        self.header_font = pygame.font.SysFont("Georgia", 45, bold=True)
        self.body_font = pygame.font.SysFont("Arial", 26)
        self.button_font = pygame.font.SysFont("Arial", 28, bold=True)

    def draw_button(self, text, y_pos):
        mouse_pos = pygame.mouse.get_pos()
        rect = pygame.Rect(WIDTH//2 - 160, y_pos, 320, 75)
        
        # Hover logic
        current_color = HOVER_COLOR if rect.collidepoint(mouse_pos) else BUTTON_COLOR
        
        # Draw button with a small gold border to match the clock aesthetic
        pygame.draw.rect(self.screen, ACCENT_COLOR, rect, border_radius=12) # Border
        pygame.draw.rect(self.screen, current_color, rect.inflate(-4, -4), border_radius=10) # Inner
        
        btn_txt = self.button_font.render(text, True, TEXT_COLOR)
        self.screen.blit(btn_txt, btn_txt.get_rect(center=rect.center))
        return rect

    def draw_start(self):
        self.screen.fill(BG_COLOR)
        
        # Title with a bit of "Shadow" for depth
        title_surf = self.title_font.render("HIDDEN", True, ACCENT_COLOR)
        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT//3)))
        
        sub_txt = self.body_font.render("Precision Escape Room", True, TEXT_COLOR)
        self.screen.blit(sub_txt, sub_txt.get_rect(center=(WIDTH//2, HEIGHT//3 + 75)))
        
        self.start_btn = self.draw_button("START GAME", HEIGHT//2 + 50)
        self.instr_btn = self.draw_button("HOW TO PLAY", HEIGHT//2 + 150)

    def draw_instructions(self):
        self.screen.fill(BG_COLOR)
        
        header = self.header_font.render("HOW TO ESCAPE", True, ACCENT_COLOR)
        self.screen.blit(header, (60, 100))
        
        # Instructions broken into smaller chunks to fit the screen width
        instr_text = [
            "• SEARCH: Click objects in the room to",
            "  find hidden mini-games.",
            "",
            "• PLAY: Complete each game to earn",
            "   a unique puzzle piece.",
            "",
            "• DIFFICULTY: Each game varies in challenge",
            "  and the precision required.",
            "",
            "• ASSEMBLE: Once all pieces are found,",
            "  complete the final puzzle to escape."
        ]
        
        # Draw instructions with proper margins
        for i, line in enumerate(instr_text):
            surf = self.body_font.render(line, True, TEXT_COLOR)
            self.screen.blit(surf, (60, 200 + (i * 45)))
            
        self.back_btn = self.draw_button("BACK", HEIGHT - 150)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == START:
                        if self.start_btn.collidepoint(event.pos):
                            print("Launching Gameplay...") 
                        elif self.instr_btn.collidepoint(event.pos):
                            self.state = INSTRUCTIONS
                    
                    elif self.state == INSTRUCTIONS:
                        if self.back_btn.collidepoint(event.pos):
                            self.state = START

            if self.state == START:
                self.draw_start()
            elif self.state == INSTRUCTIONS:
                self.draw_instructions()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    menu = HiddenMenu()
    menu.run()