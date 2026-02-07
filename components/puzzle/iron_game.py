import pygame, random, math, sys

WIDTH, HEIGHT = 900, 500
FPS = 60

WHITE=(255,255,255)
PATH=(170,190,230)
PATH_OK=(120,210,160)
IRON=(230,230,240)
ACCENT=(120,150,255)

def clamp(v,a,b): return max(a,min(b,v))
def dist(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])

class Iron:
    def __init__(self, pos):
        self.pos=list(pos)
        self.small=0.75
        self.large=1.25
        self.scale=self.small
        self.drag=False
        self.base=(96,56)

    @property
    def rect(self):
        w,h=int(self.base[0]*self.scale), int(self.base[1]*self.scale)
        return pygame.Rect(self.pos[0]-w//2, self.pos[1]-h//2, w, h)

    def handle(self,e):
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.rect.collidepoint(e.pos):
            self.scale = self.large if self.scale==self.small else self.small
            self.drag=True
        if e.type==pygame.MOUSEBUTTONUP and e.button==1:
            self.drag=False
        if e.type==pygame.MOUSEMOTION and self.drag:
            self.pos=[clamp(e.pos[0],0,WIDTH), clamp(e.pos[1],0,HEIGHT)]

    def draw(self,s):
        r=self.rect
        pygame.draw.rect(s, IRON, r, border_radius=14)
        pygame.draw.rect(s, ACCENT, r.inflate(-r.w*0.35, -r.h*0.6), border_radius=10)

def build_path(cloth, difficulty):
    npts = [6, 9, 13][difficulty-1]
    width = [44, 32, 22][difficulty-1]
    x0, x1 = cloth.x+60, cloth.right-60

    pts=[]
    for i in range(npts):
        t=i/(npts-1)
        x=int(x0+t*(x1-x0))
        y=int(cloth.centery + random.randint(-int(cloth.h*0.30), int(cloth.h*0.30)))
        pts.append((x,y))
    pts[0]=(x0, cloth.centery)
    pts[-1]=(x1, cloth.centery)
    return pts, width

def point_seg_dist(p,a,b):
    px,py=p; ax,ay=a; bx,by=b
    abx,aby=bx-ax,by-ay
    apx,apy=px-ax,py-ay
    ab2=abx*abx+aby*aby
    if ab2==0: return dist(p,a),0.0
    t=(apx*abx+apy*aby)/ab2
    t=max(0.0,min(1.0,t))
    cx,cy=ax+t*abx, ay+t*aby
    return dist(p,(cx,cy)), t

def nearest_progress(p, pts):
    total=0.0
    lens=[]
    for i in range(len(pts)-1):
        L=dist(pts[i],pts[i+1])
        lens.append(L); total+=L
    if total<=0: return 0.0, 1e9

    best_d=1e9
    best_prog=0.0
    walked=0.0
    for i in range(len(pts)-1):
        d,t=point_seg_dist(p, pts[i], pts[i+1])
        if d<best_d:
            best_d=d
            best_prog=(walked + t*lens[i]) / total
        walked += lens[i]
    return best_prog, best_d

def ironing_minigame_path(difficulty=2):
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    clock=pygame.time.Clock()

    cloth=pygame.Rect(160,90,600,320)
    pts, path_w = build_path(cloth, difficulty)
    tolerance = path_w * 0.45

    iron=Iron((80, HEIGHT//2))
    pressed=pygame.Surface(cloth.size, pygame.SRCALPHA)

    progress=0.0
    goal=0.985

    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                pygame.quit(); return False
            iron.handle(e)

        if cloth.collidepoint(iron.rect.center):
            x=iron.rect.centerx-cloth.x
            y=iron.rect.centery-cloth.y
            pygame.draw.circle(pressed,(255,255,255,35),(x,y),int(18*iron.scale))

        prog, d = nearest_progress(iron.rect.center, pts)
        on_path = d <= tolerance
        if on_path:
            progress = max(progress, prog)

        screen.fill((200,220,255))  # remove/override in your main
        pygame.draw.rect(screen, WHITE, cloth, border_radius=18)
        screen.blit(pressed, cloth.topleft)

        pygame.draw.lines(screen, PATH_OK if on_path else PATH, False, pts, path_w)

        bar=pygame.Rect(cloth.x, cloth.bottom+16, cloth.w, 10)
        pygame.draw.rect(screen, (210,220,240), bar, border_radius=8)
        pygame.draw.rect(screen, (120,210,160),
                         (bar.x, bar.y, int(bar.w*progress), bar.h),
                         border_radius=8)

        iron.draw(screen)
        pygame.display.flip()

        if progress >= goal:
            pygame.time.delay(250)
            pygame.quit()
            return True

# call:
ironing_minigame_path(difficulty=1|2|3)
