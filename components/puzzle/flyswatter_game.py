import pygame, sys, random, math, os

def fly_swatter_game():
    W, H, FPS = 1000, 650, 60
    PLAY = pygame.Rect(70, 90, W - 140, H - 160)

    MIN_FLIES, MAX_FLIES = 8, 14
    WANDER = 140
    MAX_SPEED = 360
    SWING_COOLDOWN = 0.12

    HIT_W, HIT_H = 160, 160
    HIT_OFFSET_X = 0
    HIT_OFFSET_Y = -85

    FLY_SIZE = (36, 36)
    SWATTER_SIZE = (220, 220)

    def vlen(x, y): return math.hypot(x, y)

    def load_image(name):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
        return pygame.image.load(path).convert_alpha()

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 44, bold=True)

    fly_img = pygame.transform.smoothscale(load_image("fly.png"), FLY_SIZE)
    swatter_img = pygame.transform.smoothscale(load_image("swatter.png"), SWATTER_SIZE)

    # Transparent overlay for any text (guaranteed no background box)
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)

    class Fly:
        def __init__(self):
            self.alive = True
            self.pos = [random.uniform(PLAY.left + 20, PLAY.right - 20),
                        random.uniform(PLAY.top + 20, PLAY.bottom - 20)]
            sp = random.uniform(140, 320)
            ang = random.uniform(0, math.tau)
            self.vx = math.cos(ang) * sp
            self.vy = math.sin(ang) * sp
            self.t = random.uniform(0, 10)
            self.angle = 0.0
            self.scale = random.uniform(0.85, 1.15)

        def update(self, dt):
            self.t += dt * random.uniform(1.6, 2.4)
            self.vx += math.cos(self.t) * WANDER * dt
            self.vy += math.sin(self.t * 1.2) * WANDER * dt

            sp = vlen(self.vx, self.vy)
            if sp > MAX_SPEED:
                k = MAX_SPEED / sp
                self.vx *= k
                self.vy *= k

            self.pos[0] += self.vx * dt
            self.pos[1] += self.vy * dt

            if self.pos[0] < PLAY.left:
                self.pos[0] = PLAY.left
                self.vx *= -1
            if self.pos[0] > PLAY.right:
                self.pos[0] = PLAY.right
                self.vx *= -1
            if self.pos[1] < PLAY.top:
                self.pos[1] = PLAY.top
                self.vy *= -1
            if self.pos[1] > PLAY.bottom:
                self.pos[1] = PLAY.bottom
                self.vy *= -1

            if abs(self.vx) + abs(self.vy) > 5:
                self.angle = math.degrees(math.atan2(-self.vy, self.vx))

        def draw(self, s):
            x, y = int(self.pos[0]), int(self.pos[1])
            img = fly_img
            if self.scale != 1.0:
                img = pygame.transform.smoothscale(
                    fly_img,
                    (int(FLY_SIZE[0] * self.scale), int(FLY_SIZE[1] * self.scale))
                )
            rot = pygame.transform.rotate(img, self.angle)
            s.blit(rot, rot.get_rect(center=(x, y)))

    class Swatter:
        def __init__(self):
            self.pos = (0, 0)
            self.swing = 0.0
            self.cooldown = 0.0

        def update(self, dt):
            self.pos = pygame.mouse.get_pos()
            self.cooldown = max(0.0, self.cooldown - dt)
            self.swing = max(0.0, self.swing - dt * 6.0)

        def can_swing(self):
            return self.cooldown <= 0.0

        def swing_now(self):
            self.swing = 1.0
            self.cooldown = SWING_COOLDOWN

        def hit_rect(self):
            x, y = self.pos
            cx = x + HIT_OFFSET_X
            cy = y + HIT_OFFSET_Y
            return pygame.Rect(cx - HIT_W // 2, cy - HIT_H // 2, HIT_W, HIT_H)

        def draw(self, s):
            x, y = self.pos
            rot = pygame.transform.rotate(swatter_img, -18 * self.swing)
            s.blit(rot, rot.get_rect(center=(x, y)))

    def new_round():
        return [Fly() for _ in range(random.randint(MIN_FLIES, MAX_FLIES))]

    flies = new_round()
    swatter = Swatter()
    won = False

    while True:
        dt = clock.tick(FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); return
                if e.key == pygame.K_r:
                    flies = new_round()
                    won = False

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not won:
                if swatter.can_swing():
                    swatter.swing_now()
                    hitbox = swatter.hit_rect()
                    for f in flies:
                        if f.alive and hitbox.collidepoint(int(f.pos[0]), int(f.pos[1])):
                            f.alive = False

        swatter.update(dt)

        if not won:
            for f in flies:
                if f.alive:
                    f.update(dt)
            if all(not f.alive for f in flies):
                won = True

        # IMPORTANT: Don't try to "transparent fill" the display.
        # Use a normal fill (or replace with your main game's draw).
        screen.fill((0, 0, 0))

        for f in flies:
            if f.alive:
                f.draw(screen)
        swatter.draw(screen)

        if won:
            overlay.fill((0, 0, 0, 0))  # transparent overlay
            text = font.render("DONE!", True, (0, 255, 0))  # green, transparent background
            overlay.blit(text, text.get_rect(center=(W // 2, H // 2)))
            screen.blit(overlay, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    fly_swatter_game()
