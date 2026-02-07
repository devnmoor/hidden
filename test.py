import pygame, sys, math, os

def duck_bathtub_game(sprite_path, max_shots=12):
    W, H, FPS = 1000, 650, 60

    def clamp(v,a,b): return max(a, min(b, v))
    def vlen(v): return math.hypot(v[0], v[1])
    def vsub(a,b): return (a[0]-b[0], a[1]-b[1])
    def vmul(v,k): return (v[0]*k, v[1]*k)
    def vnorm(v):
        L=vlen(v)
        return (0,0) if L==0 else (v[0]/L, v[1]/L)

    def circle_rect_hit(cx, cy, r, rect):
        px = clamp(cx, rect.left, rect.right)
        py = clamp(cy, rect.top, rect.bottom)
        dx, dy = cx - px, cy - py
        return (dx*dx + dy*dy) <= r*r, (px, py), (dx, dy)

    class Duck:
        def __init__(self, pos, r=22):
            self.r = r
            self.reset(pos)

        def reset(self, pos):
            self.pos = [float(pos[0]), float(pos[1])]
            self.vel = [0.0, 0.0]
            self.launched = False
            self.sleep = 0

        @property
        def rect(self):
            return pygame.Rect(int(self.pos[0]-self.r), int(self.pos[1]-self.r), self.r*2, self.r*2)

        def launch(self, vel):
            self.vel[0], self.vel[1] = vel
            self.launched = True
            self.sleep = 0

        def step(self, dt, gravity, solids, bounds):
            # integrate
            self.vel[1] += gravity * dt
            self.pos[0] += self.vel[0] * dt
            self.pos[1] += self.vel[1] * dt

            left, top, right, bottom = bounds
            rest, fric = 0.50, 0.94

            # screen bounds
            if self.pos[0] < left + self.r:
                self.pos[0] = left + self.r
                self.vel[0] *= -rest
                self.vel[1] *= fric
            if self.pos[0] > right - self.r:
                self.pos[0] = right - self.r
                self.vel[0] *= -rest
                self.vel[1] *= fric
            if self.pos[1] < top + self.r:
                self.pos[1] = top + self.r
                self.vel[1] *= -rest
                self.vel[0] *= fric
            if self.pos[1] > bottom - self.r:
                self.pos[1] = bottom - self.r
                self.vel[1] *= -rest
                self.vel[0] *= fric

            # tub collisions
            for s in solids:
                hit, closest, dxy = circle_rect_hit(self.pos[0], self.pos[1], self.r, s["rect"])
                if not hit:
                    continue

                dx, dy = dxy
                if dx == 0 and s["rect"].left < self.pos[0] < s["rect"].right: dx = 1e-6
                if dy == 0 and s["rect"].top < self.pos[1] < s["rect"].bottom: dy = 1e-6

                rest = s.get("rest", 0.55)
                fric = s.get("fric", 0.94)

                if abs(dx) > abs(dy):
                    self.pos[0] = closest[0] - self.r if self.pos[0] < closest[0] else closest[0] + self.r
                    self.vel[0] *= -rest
                    self.vel[1] *= fric
                else:
                    self.pos[1] = closest[1] - self.r if self.pos[1] < closest[1] else closest[1] + self.r
                    self.vel[1] *= -rest
                    self.vel[0] *= fric

            # settle detection (reset after shot ends)
            if abs(self.vel[0]) < 35 and abs(self.vel[1]) < 35:
                self.sleep += 1
            else:
                self.sleep = 0

        def update(self, dt, gravity, solids, bounds):
            if not self.launched:
                return
            # Substeps = smoother motion + stable collisions
            substeps = 3
            step_dt = dt / substeps
            for _ in range(substeps):
                self.step(step_dt, gravity, solids, bounds)

        def draw(self, surf):
            x, y = int(self.pos[0]), int(self.pos[1])
            pygame.draw.circle(surf, (255,210,70), (x,y), self.r)
            pygame.draw.circle(surf, (255,230,120), (x-self.r//4,y-self.r//4), self.r//2)
            pygame.draw.circle(surf, (245,155,70), (x+self.r-6,y+4), max(6,self.r//4))
            pygame.draw.circle(surf, (70,80,95), (x-self.r//6,y-self.r//6), max(3,self.r//8))

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)

    # If you want to force local assets folder, uncomment:
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # sprite_path = os.path.join(BASE_DIR, "assets", "bathtub.png")

    tub_img = pygame.image.load(sprite_path).convert_alpha()
    tub_img = pygame.transform.smoothscale(tub_img, (520, 340))
    tub_rect = tub_img.get_rect(center=(W - 280, H//2 + 10))

    # Static hitboxes (tuned for this sprite size)
    rim = pygame.Rect(tub_rect.x + 70,  tub_rect.y + 82,  tub_rect.w - 140, 18)
    left_wall = pygame.Rect(tub_rect.x + 70,  tub_rect.y + 90,  22, tub_rect.h - 130)
    right_wall = pygame.Rect(tub_rect.right - 92, tub_rect.y + 90, 22, tub_rect.h - 130)
    bottom_lip = pygame.Rect(tub_rect.x + 95,  tub_rect.bottom - 105, tub_rect.w - 190, 22)
    solids = [
        {"rect": rim, "rest": 0.62, "fric": 0.95},
        {"rect": left_wall, "rest": 0.50, "fric": 0.92},
        {"rect": right_wall, "rest": 0.50, "fric": 0.92},
        {"rect": bottom_lip, "rest": 0.30, "fric": 0.90},
    ]

    # WATER SENSOR (touch = instant win)
    water = pygame.Rect(tub_rect.x + 120, tub_rect.y + 130, tub_rect.w - 240, tub_rect.h - 210)

    duck_start = (160, H - 140)
    duck = Duck(duck_start, r=22)

    # Smoother + slower
    gravity = 1100.0     # was 1800
    sling_max = 220      # was 260 (limits extreme shots)
    power = 4.8          # was 7.0 (slower throw)

    dragging = False
    drag_start = (0,0)
    drag_now = (0,0)

    shots = 0
    bounds = (0, 0, W, H)

    preview_steps = 28
    preview_dt = 0.07    # slightly slower preview for readability

    won = False

    while True:
        dt = clock.tick(FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); return won
                if e.key == pygame.K_r:
                    shots = 0
                    won = False
                    duck.reset(duck_start)

            if won:
                continue

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if (not duck.launched) and duck.rect.collidepoint(e.pos) and shots < max_shots:
                    dragging = True
                    drag_start = e.pos
                    drag_now = e.pos

            if e.type == pygame.MOUSEMOTION and dragging:
                drag_now = e.pos

            if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and dragging:
                dragging = False
                pull = vsub(drag_start, drag_now)  # pull back to shoot forward
                L = vlen(pull)
                if L > 10:
                    if L > sling_max:
                        pull = vmul(vnorm(pull), sling_max)
                    duck.launch((pull[0]*power, pull[1]*power))
                    shots += 1

        if not won:
            duck.update(dt, gravity, solids, bounds)

            # INSTANT WIN: duck touches water region
            if duck.launched and water.collidepoint(int(duck.pos[0]), int(duck.pos[1])):
                won = True

            # reset duck after it settles (if not won)
            if duck.launched and duck.sleep > 30 and not won:
                duck.reset(duck_start)

        # draw
        screen.fill((210, 235, 255))
        screen.blit(tub_img, tub_rect)

        # trajectory preview while dragging
        if dragging and not won:
            pull = vsub(drag_start, drag_now)
            L = vlen(pull)
            if L > 4:
                if L > sling_max:
                    pull = vmul(vnorm(pull), sling_max)
                vx, vy = pull[0]*power, pull[1]*power
                px, py = duck.pos[0], duck.pos[1]
                pvx, pvy = vx, vy
                for _ in range(preview_steps):
                    pvy += gravity * preview_dt
                    px += pvx * preview_dt
                    py += pvy * preview_dt
                    pygame.draw.circle(screen, (120,170,255), (int(px), int(py)), 4)

        duck.draw(screen)

        ui = font.render(f"Shots {shots}/{max_shots}", True, (40,55,80))
        screen.blit(ui, (20, 18))

        if won:
            msg = font.render("WIN! Duck touched water.  (R) Restart  (ESC) Exit", True, (40,55,80))
            screen.blit(msg, (20, 48))

        pygame.display.flip()

if __name__ == "__main__":
    # IMPORTANT: use your real mac path or local relative path
    # Example if bathtub.png is next to this file:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sprite = os.path.join(BASE_DIR, "bathtub.png")
    duck_bathtub_game(sprite, max_shots=12)