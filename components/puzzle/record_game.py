import pygame, sys, math, random, os

def record_player_game(difficulty=3, needle_length=240):
    W, H, FPS = 1000, 650, 60
    CENTER = (W // 2, H // 2)

    # Colors
    BG = (18, 22, 28)
    ARM = (210, 220, 235)
    NEEDLE = (245, 215, 125)
    DOT = (255, 90, 120)
    GREEN = (0, 255, 0)
    RED = (255, 70, 70)

    # Difficulty
    dot_radius = {1: 16, 2: 12, 3: 9}[difficulty]
    hit_margin = {1: 10, 2: 8, 3: 6}[difficulty]
    lower_speed = {1: 0.60, 2: 0.45, 3: 0.34}[difficulty]
    spin_speed = {1: 1.1, 2: 1.6, 3: 2.2}[difficulty]

    def clamp(v, a, b):
        return max(a, min(b, v))

    def dist(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def load_record_frames(prefix="record", count=8, target_diameter=None):
        """
        Loads record0.png ... record7.png with transparency.
        If images have a solid background (no alpha), we auto-colorkey using top-left pixel.
        """
        frames = []
        for i in range(count):
            path = f"{prefix}{i}.png"
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing image: {path}")

            img = pygame.image.load(path)

            # If no alpha channel, use top-left pixel as a color key background
            if img.get_alpha() is None and (img.get_flags() & pygame.SRCALPHA) == 0:
                img = img.convert()
                key = img.get_at((0, 0))
                img.set_colorkey(key)
                img = img.convert_alpha()
            else:
                img = img.convert_alpha()

            if target_diameter is not None:
                img = pygame.transform.smoothscale(img, (target_diameter, target_diameter))

            frames.append(img)
        return frames

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Record Player")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 44, bold=True)

    # --- Record animation frames ---
    record_frames = load_record_frames(prefix="record", count=8, target_diameter=None)
    frame_count = len(record_frames)

    # Record radius from image size
    rw, rh = record_frames[0].get_size()
    RECORD_R = min(rw, rh) // 2

    # Animation timing
    frame_time = 1.0 / 12.0
    anim_t = 0.0

    # --- OVAL DOT PATH SETTINGS ---
    # User request: range 55 height and 100 width, oval motion.
    # Treat as semi-axes: a = 100 (x radius), b = 55 (y radius).
    OVAL_A = 100
    OVAL_B = 55

    # Keep dot fully inside the oval by shrinking axes by dot radius
    a_in = max(1, OVAL_A - dot_radius)
    b_in = max(1, OVAL_B - dot_radius)

    # --- Needle placement: right of player, shorter needle ---
    arm_len = float(needle_length)

    # Place pivot to the right of the record image
    pivot = (CENTER[0] + RECORD_R + 170, CENTER[1] - 10)

    # States
    spinning_angle = 0.0
    lowering = False
    needle_h = 1.0
    won = False
    lost = False
    resolved = False

    # Dot phase random each round (random start angle on oval)
    dot_phase = 0.0

    def new_round():
        nonlocal spinning_angle, lowering, needle_h, won, lost, resolved, anim_t, dot_phase
        spinning_angle = 0.0
        lowering = False
        needle_h = 1.0
        won = False
        lost = False
        resolved = False
        anim_t = 0.0
        dot_phase = random.uniform(-math.pi, math.pi)  # random position on oval

    def tip_from_mouse(mx, my):
        """
        Arm follows mouse but is clamped to a right-side range so it behaves like a tonearm.
        """
        dx, dy = mx - pivot[0], my - pivot[1]
        ang = math.atan2(dy, dx)

        # Right-side-ish limits (tweak if you want more/less movement)
        ang = clamp(ang, -2.25, -0.15)

        tip = (pivot[0] + math.cos(ang) * arm_len,
               pivot[1] + math.sin(ang) * arm_len)
        return ang, tip

    def dot_pos():
        """
        Dot moves around an oval centered on the record CENTER.
        It rotates continuously using spinning_angle, plus a random dot_phase per round.
        """
        a = spinning_angle + dot_phase
        return (CENTER[0] + math.cos(a) * a_in,
                CENTER[1] + math.sin(a) * b_in)

    new_round()

    while True:
        dt = clock.tick(FPS) / 1000.0

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return won
                if e.key == pygame.K_r:
                    new_round()

            if not resolved:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    lowering = True
                if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    lowering = False

        if not resolved:
            spinning_angle = (spinning_angle + spin_speed * dt) % (math.tau)

            if lowering:
                needle_h = max(0.0, needle_h - lower_speed * dt)
            else:
                needle_h = min(1.0, needle_h + (lower_speed * 0.50) * dt)

        # Record frame animation (loops forever)
        anim_t += dt
        frame_idx = int(anim_t / frame_time) % frame_count

        mx, my = pygame.mouse.get_pos()
        arm_ang, tip = tip_from_mouse(mx, my)

        contact = needle_h <= 0.06
        dpos = dot_pos()

        # Win/lose once at contact moment while lowering
        if not resolved and contact and lowering:
            if dist(tip, dpos) <= (dot_radius + hit_margin):
                won = True
            else:
                lost = True
            resolved = True
            lowering = False

        # --- Draw ---
        screen.fill(BG)

        # Record image centered
        frame = record_frames[frame_idx]
        screen.blit(frame, frame.get_rect(center=CENTER))

        # Moving dot on oval path
        pygame.draw.circle(screen, DOT, (int(dpos[0]), int(dpos[1])), dot_radius)

        # Arm + needle (shorter and placed on right)
        arm_end = (pivot[0] + math.cos(arm_ang) * arm_len,
                   pivot[1] + math.sin(arm_ang) * arm_len)
        arm_end_i = (int(arm_end[0]), int(arm_end[1]))

        pivot_i = (int(pivot[0]), int(pivot[1]))
        pygame.draw.circle(screen, ARM, pivot_i, 14)
        pygame.draw.line(screen, ARM, pivot_i, arm_end_i, 10)

        tip_draw = (arm_end[0], arm_end[1] - (22 * needle_h))
        tip_draw_i = (int(tip_draw[0]), int(tip_draw[1]))
        pygame.draw.circle(screen, NEEDLE, tip_draw_i, 9 if not contact else 6)

        if won:
            t = font.render("LEVEL COMPLETE", True, GREEN)
            screen.blit(t, t.get_rect(center=(W // 2, 60)))
        elif lost:
            t = font.render("TRY AGAIN", True, RED)
            screen.blit(t, t.get_rect(center=(W // 2, 60)))

        pygame.display.flip()

if __name__ == "__main__":
    record_player_game(difficulty=3, needle_length=240)
