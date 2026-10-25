# Escape From Earth - the course, version 2.
# One long picture (what you see) plus a mask (what you crash into). Everything drawn is solid.
# Rules: ground stuff stays low (tops at y 28 or lower), the top strip belongs to air traffic (in code),
# and the big set pieces make you fly THROUGH them: tunnel, canopy, overpass, arches, cranes, cave.
import math, random, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageChops
random.seed(7)
LW, H, G = 7808, 64, 57
img = Image.new('1', (LW, H), 0); msk = Image.new('1', (LW, H), 0)
di, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
gnd = [G] * LW
SECTIONS = []                     # (start x, name) - the game uses these to pick air traffic

def P(x, y, v=1):
    if 0 <= x < LW and 0 <= y < H: img.putpixel((x, y), v)
def solid(x0, y0, x1, y1):        # mark an area as solid without drawing (for black-filled shapes)
    dm.rectangle([x0, y0, x1, y1], fill=1)
def box(x, y, w, h, fill=0):
    dm.rectangle([x, y, x + w - 1, y + h - 1], fill=1)
    di.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=1)
def poly(pts, fill=0):
    dm.polygon(pts, fill=1); di.polygon(pts, fill=fill, outline=1)
def line(x0, y0, x1, y1, w=1):
    di.line([x0, y0, x1, y1], fill=1, width=w); dm.line([x0, y0, x1, y1], fill=1, width=w)
def dither_poly(pts, step=2):     # filled with a light checker pattern
    tmp = Image.new('1', (LW, H), 0); ImageDraw.Draw(tmp).polygon(pts, fill=1)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        for x in range(max(0, min(xs)), min(LW, max(xs) + 1)):
            if tmp.getpixel((x, y)) and (x + y) % step == 0 and (y % 2 == 0): P(x, y)
    dm.polygon(pts, fill=1); di.polygon(pts, outline=1)
def window(x, y, w=5, h=5, lit=None):
    if lit is None: lit = random.random() < 0.55
    di.rectangle([x, y, x + w - 1, y + h - 1], fill=1 if lit else 0, outline=1)
    if lit:
        di.line([x + w // 2, y, x + w // 2, y + h - 1], fill=0); di.line([x, y + h // 2, x + w - 1, y + h // 2], fill=0)
        di.rectangle([x, y, x + w - 1, y + h - 1], outline=1)

# ------------------------------------------------------------------ props
def house(x, w=30, h=14, roof=9, style=0):
    """Clapboard house: siding, shingled roof, chimney, door with porch, framed windows."""
    gy = G
    box(x, gy - h, w, h)
    for yy in range(gy - h + 3, gy - 1, 3):                    # siding
        for xx in range(x + 2, x + w - 2, 2): P(xx, yy)
    rp = [(x - 3, gy - h), (x + w // 2, gy - h - roof), (x + w + 2, gy - h)]
    dither_poly(rp)
    cx = x + w - 9; box(cx, gy - h - roof + 1, 4, roof - 2); di.line([cx - 1, gy - h - roof + 1, cx + 4, gy - h - roof + 1], fill=1)
    dx = x + 4 + (style % 2) * (w - 13)                        # door
    di.rectangle([dx, gy - 9, dx + 4, gy - 1], fill=0, outline=1); P(dx + 3, gy - 5)
    di.line([dx - 2, gy - 11, dx + 6, gy - 11], fill=1); P(dx - 2, gy - 10); P(dx + 6, gy - 10)   # porch roof
    for wx in range(x + 3, x + w - 6, 9):
        if abs(wx - dx) > 6: window(wx, gy - h + 3, 5, 5)
def tree(x, r=7, trunk=6):
    gy = gnd[x]; cy = gy - trunk - r
    di.rectangle([x - 1, gy - trunk - 2, x, gy - 1], fill=1); solid(x - 1, gy - trunk - 2, x, gy - 1)
    dm.ellipse([x - r, cy - r, x + r, cy + r], fill=1)
    di.ellipse([x - r, cy - r, x + r, cy + r], fill=0, outline=1)
    for yy in range(cy - r + 2, cy + r - 1):
        for xx in range(x - r + 2, x + r - 1):
            if ((xx - x) ** 2 + (yy - cy) ** 2) < (r - 2) ** 2 and (xx * 3 + yy * 5) % 7 == 0: P(xx, yy)
def pine(x, h=20):
    gy = gnd[x]
    for k in range(3):
        y0 = gy - h + k * (h // 4); hw = 4 + k * 2
        dither_poly([(x, y0), (x - hw, y0 + h // 3), (x + hw, y0 + h // 3)])
    di.rectangle([x - 1, gy - h // 4, x, gy - 1], fill=1); solid(x - 1, gy - h // 4, x, gy - 1)
def car(x, y=G, truck=False):
    if truck:
        box(x, y - 11, 16, 9); box(x + 16, y - 8, 7, 6); window(x + 18, y - 7, 3, 3, True)
        for wx in (x + 3, x + 12, x + 19): di.ellipse([wx - 2, y - 4, wx + 2, y], fill=0, outline=1); solid(wx - 2, y - 4, wx + 2, y)
        return
    poly([(x, y - 3), (x + 2, y - 6), (x + 5, y - 8), (x + 11, y - 8), (x + 13, y - 6), (x + 16, y - 5), (x + 16, y - 2), (x, y - 2)])
    di.line([x + 6, y - 7, x + 6, y - 6], fill=1); di.line([x + 10, y - 7, x + 10, y - 6], fill=1)
    for wx in (x + 4, x + 12): di.ellipse([wx - 2, y - 4, wx + 2, y], fill=0, outline=1); solid(wx - 2, y - 4, wx + 2, y)
def fence(x0, x1, y=G):
    for xx in range(x0, x1, 6): line(xx, y - 5, xx, y - 1)
    line(x0, y - 4, x1 - 6, y - 4); line(x0, y - 2, x1 - 6, y - 2)
def lamp(x, h=18):
    line(x, G - h, x, G - 1); line(x, G - h, x + 4, G - h); box(x + 3, G - h, 3, 2, 1)
def poles(x0, x1, step=60, h=24):
    for xx in range(x0, x1 + 1, step): line(xx, G - h, xx, G - 1); line(xx - 3, G - h + 2, xx + 3, G - h + 2)
    for xx in range(x0, x1, step):
        for i in range(step + 1):
            yy = G - h + 2 + int(4 * math.sin(i / step * math.pi)); P(xx + i, yy); dm.point((xx + i, yy), 1)

# ------------------------------------------------------------------ 1. the farm (0-950)
SECTIONS.append((0, 'farm'))
box(48, G - 3, 36, 3, 1); [P(k, G - 4) for k in range(52, 84, 6)]
# barn with a gambrel roof
bx = 110; box(bx, G - 18, 36, 18)
dither_poly([(bx - 2, G - 18), (bx + 4, G - 26), (bx + 32, G - 26), (bx + 38, G - 18)])
di.rectangle([bx + 13, G - 14, bx + 23, G - 1], fill=0, outline=1); di.line([bx + 13, G - 14, bx + 23, G - 1], fill=1); di.line([bx + 23, G - 14, bx + 13, G - 1], fill=1)
di.rectangle([bx + 15, G - 24, bx + 21, G - 20], fill=0, outline=1)
# silo
box(152, G - 21, 12, 21); di.chord([152, G - 26, 163, G - 16], 180, 360, fill=0, outline=1); dm.chord([152, G - 26, 163, G - 16], 180, 360, fill=1)
for yy in range(G - 17, G, 5): di.line([153, yy, 162, yy], fill=1)
fence(175, 260)
# hay bales
for hx in (190, 204, 197):
    hy = G if hx != 197 else G - 7
    di.ellipse([hx, hy - 7, hx + 9, hy - 1], fill=0, outline=1); dm.ellipse([hx, hy - 7, hx + 9, hy - 1], fill=1); P(hx + 4, hy - 4); P(hx + 5, hy - 4)
# tractor
tx = 280; box(tx, G - 9, 14, 5); box(tx + 8, G - 15, 7, 6); window(tx + 9, G - 14, 5, 4, True)
di.ellipse([tx - 1, G - 7, tx + 5, G - 1], fill=0, outline=1); dm.ellipse([tx - 1, G - 7, tx + 5, G - 1], fill=1)
di.ellipse([tx + 8, G - 10, tx + 17, G - 1], fill=0, outline=1); dm.ellipse([tx + 8, G - 10, tx + 17, G - 1], fill=1); P(tx + 12, G - 6)
house(330, 34, 15, 10)
tree(390, 8, 7); tree(410, 6, 6)
# scarecrow in the crops
for cx in range(440, 560, 5): P(cx, G - 2); P(cx + 2, G - 3)
line(500, G - 16, 500, G - 1); line(494, G - 12, 506, G - 12); di.ellipse([497, G - 20, 503, G - 15], fill=0, outline=1); dm.ellipse([497, G - 20, 503, G - 15], fill=1)
line(495, G - 21, 505, G - 21)
# water pump windmill
line(600, G - 20, 596, G - 1); line(600, G - 20, 604, G - 1); line(597, G - 8, 603, G - 8)
for a in range(0, 360, 45):
    r = math.radians(a); line(600, G - 21, 600 + int(6 * math.cos(r)), G - 21 + int(6 * math.sin(r)))
house(640, 28, 13, 9, 1); tree(690, 7, 6)
fence(710, 820)
tree(850, 9, 7); tree(880, 7, 6); pine(905, 22); pine(925, 18)

# ------------------------------------------------------------------ 2. railway and mountain tunnel (950-1900)
SECTIONS.append((950, 'country'))
RY = G - 2
for xx in range(950, 1900): P(xx, RY)
for xx in range(952, 1900, 4): P(xx, RY + 1)
# mountain: solid from the top down to the tunnel roof; the tunnel is the only way through
M0, M1 = 1150, 1650
for xx in range(M0 - 110, M1 + 111):
    if xx < M0: top = int(G - (xx - (M0 - 110)) / 110 * (G - 38))           # foothill rising to y 38
    elif xx > M1: top = int(38 + (xx - M1) / 110 * (G - 38))
    else: top = 0
    top += int(1.5 * math.sin(xx / 5))
    if M0 <= xx <= M1:                                                     # rock over the tunnel
        roof = 17 + int(2 * math.sin(xx / 23))
        dm.line([xx, 0, xx, roof], fill=1); P(xx, roof)
        for k in range(2, roof - 1, 4):
            if (xx * 7 + k * 3) % 11 == 0: P(xx, k)
    else:                                                                  # foothill: solid down to the ground
        gnd[xx] = max(0, min(G, top))
for ex in (M0, M1):                                                        # cliff faces with a stone tunnel mouth
    di.line([ex, 0, ex, 19], fill=1); dm.line([ex, 0, ex, 19], fill=1)
    for k in range(0, 18, 3): P(ex + (2 if ex == M0 else -2), k + 1)
pine(1010, 18); pine(1028, 14); pine(1790, 18); pine(1810, 14); tree(1840, 7, 6)
# a freight train sitting in the tunnel
lx = 1250; box(lx, G - 12, 22, 10); box(lx + 14, G - 17, 8, 5); window(lx + 15, G - 16, 6, 3, True); box(lx + 2, G - 15, 3, 3)
for k in range(5):
    cx0 = lx + 25 + k * 24; box(cx0, G - 11, 22, 9)
    for yy in range(G - 9, G - 3, 2): di.line([cx0 + 2, yy, cx0 + 19, yy], fill=1)
for wx in range(lx + 3, lx + 25 + 5 * 24, 7): di.ellipse([wx - 2, G - 4, wx + 2, G], fill=0, outline=1); solid(wx - 2, G - 4, wx + 2, G)
lamp(1820); lamp(1880)

# ------------------------------------------------------------------ 3. small town with a gas station (1900-2900)
SECTIONS.append((1900, 'town'))
house(1920, 30, 14, 9); house(1965, 26, 16, 10, 1)
# gas station: fly under the canopy or over it
gx = 2030
box(gx, 34, 56, 3)                                                    # canopy
di.rectangle([gx + 2, 31, gx + 22, 33], fill=1); solid(gx + 2, 31, gx + 22, 33)   # sign band on top
line(gx + 6, 37, gx + 6, G - 1, 2); line(gx + 48, 37, gx + 48, G - 1, 2)
for px_ in (gx + 18, gx + 32): box(px_, G - 9, 5, 9); P(px_ + 2, G - 7)
box(gx + 64, G - 14, 30, 14); window(gx + 68, G - 11, 8, 6, True); di.rectangle([gx + 82, G - 10, gx + 87, G - 1], fill=0, outline=1)
line(gx + 100, 38, gx + 100, G - 1); box(gx + 95, 31, 12, 8)
car(gx + 10);
house(2160, 28, 13, 8); tree(2200, 6, 5); house(2220, 32, 15, 10, 1)
# church
ch = 2290; box(ch, G - 15, 28, 15); dither_poly([(ch - 2, G - 15), (ch + 14, G - 21), (ch + 30, G - 15)])
box(ch + 18, G - 20, 8, 5); poly([(ch + 17, G - 20), (ch + 22, G - 24), (ch + 27, G - 20)])
line(ch + 22, G - 27, ch + 22, G - 24); line(ch + 20, G - 26, ch + 24, G - 26)
di.arc([ch + 4, G - 12, ch + 10, G - 4], 180, 360, fill=1); di.rectangle([ch + 4, G - 8, ch + 10, G - 1], outline=1)
# water tower: fly between the legs, under the tank
wt = 2360; box(wt, 36, 30, 8); di.ellipse([wt, 32, wt + 29, 40], fill=0, outline=1); dm.ellipse([wt, 32, wt + 29, 40], fill=1)
for yy in range(38, 43, 3): [P(xx, yy) for xx in range(wt + 2, wt + 28, 2)]
line(wt + 4, 44, wt + 4, G - 1, 2); line(wt + 25, 44, wt + 25, G - 1, 2); line(wt + 4, 50, wt + 25, 50)
poles(2420, 2600, 60, 22)
house(2440, 30, 14, 9); car(2480); house(2510, 26, 13, 8, 1); tree(2550, 7, 6); house(2575, 30, 15, 10)
# a little main street block
for k, (w, h) in enumerate(((22, 22), (18, 18), (26, 24), (20, 20))):
    bx0 = 2640 + sum(v[0] + 4 for v in ((22, 22), (18, 18), (26, 24), (20, 20))[:k])
    box(bx0, G - h, w, h); di.line([bx0, G - h + 3, bx0 + w - 1, G - h + 3], fill=1)
    for wy in range(G - h + 6, G - 8, 7):
        for wx in range(bx0 + 2, bx0 + w - 5, 6): window(wx, wy, 4, 4)
    di.rectangle([bx0 + w // 2 - 3, G - 7, bx0 + w // 2 + 2, G - 1], fill=0, outline=1)
car(2745, truck=True); lamp(2780); tree(2810, 6, 5); lamp(2850)

# ------------------------------------------------------------------ 4. highway overpass (2900-3700)
SECTIONS.append((2900, 'highway'))
DY = 43                                                                # deck top: fly over it, under the planes
box(2920, DY, 760, 4)
for xx in range(2922, 3678, 12): line(xx, DY - 3, xx, DY - 1)         # railing
di.line([2922, DY - 3, 3677, DY - 3], fill=1); dm.line([2922, DY - 3, 3677, DY - 3], fill=1)
for pxl in range(2960, 3680, 90):                                      # pillars
    box(pxl, DY + 4, 7, G - DY - 4)
poly([(2880, G), (2920, DY), (2920, G)]); poly([(3680, DY), (3720, G), (3680, G)])   # ramps
for k, cxp in enumerate(range(2960, 3640, 64)):                        # traffic on the deck
    car(cxp + random.randint(0, 18), y=DY - 1, truck=(k % 3 == 1))
for xx in range(2900, 3700, 12): P(xx, G + 3); P(xx + 1, G + 3)

# ------------------------------------------------------------------ 5. carnival (3700-4400)
SECTIONS.append((3700, 'carnival'))
for tx0 in (3720, 3790):                                               # striped tents
    poly([(tx0, G - 1), (tx0 + 12, G - 18), (tx0 + 24, G - 1)])
    for k in range(1, 6): di.line([tx0 + 12, G - 18, tx0 + k * 4, G - 1], fill=1)
    line(tx0 + 12, G - 22, tx0 + 12, G - 18); P(tx0 + 13, G - 21); P(tx0 + 14, G - 21)
# ferris wheel
fx, fy, fr = 3880, 43, 12
di.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], outline=1); dm.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], outline=1)
for a in range(0, 360, 45):
    r = math.radians(a); ex, ey = fx + int(fr * math.cos(r)), fy + int(fr * math.sin(r))
    line(fx, fy, ex, ey); box(ex - 2, ey, 5, 4)
line(fx, fy, fx - 9, G - 1, 2); line(fx, fy, fx + 9, G - 1, 2)
# roller coaster: big humps you fly over, supports underneath
cpts = []
for xx in range(3960, 4260):
    yy = int(40 - 10 * math.sin((xx - 3960) / 300 * math.pi * 3) ** 2)
    cpts.append((xx, yy))
for (xx, yy) in cpts: P(xx, yy); P(xx, yy + 2); dm.line([xx, yy, xx, yy + 2], fill=1)
for (xx, yy) in cpts[::12]: line(xx, yy + 3, xx, G - 1); P(xx, yy + 1)
box(4105, 30, 8, 5)                                                   # a coaster car on top
# coaster station: the track comes out of it, with a striped awning and a sign
st0 = 3922
box(st0, G - 17, 38, 17)
dither_poly([(st0 - 3, G - 17), (st0 + 4, G - 23), (st0 + 34, G - 23), (st0 + 41, G - 17)])
for k in range(st0 + 2, st0 + 36, 6): di.line([k, G - 17, k + 3, G - 14], fill=1)       # awning scallops
di.rectangle([st0 + 26, 41, st0 + 37, 46], fill=0, outline=1)                            # tunnel mouth where the track leaves
for k in range(st0 + 4, st0 + 22, 5): window(k, G - 11, 3, 4)
di.rectangle([st0 + 10, G - 27, st0 + 26, G - 24], fill=1); solid(st0 + 10, G - 27, st0 + 26, G - 24)
for k in range(st0 + 12, st0 + 25, 3): P(k, G - 26, 0)
# the track ends in a little shed at the far end
box(4255, 36, 18, G - 36); dither_poly([(4253, 36), (4264, 31), (4275, 36)])
house(4290, 26, 12, 7); tree(4330, 7, 6); box(4350, G - 10, 20, 10); [P(xx, G - 12) for xx in range(4350, 4370, 2)]

# ------------------------------------------------------------------ 6. downtown with arch towers (4400-5400)
SECTIONS.append((4400, 'city'))
x = 4420
for k in range(14):
    r = k % 4
    w = random.randint(18, 30); top = random.randint(30, 42) + (10 if r == 3 else 6 if r == 0 else 3)
    box(x, top, w, G - top)
    di.line([x, top + 2, x + w - 1, top + 2], fill=1)
    for wy in range(top + 5, G - 4, 5):
        for wx in range(x + 2, x + w - 3, 5): window(wx, wy, 3, 3)                                                          # something on the roof
    if r == 0: box(x + 3, top - 5, 6, 5); line(x + 4, top - 7, x + 7, top - 7)                 # water tank
    elif r == 1: box(x + w - 8, top - 3, 5, 3)                                                 # air con
    elif r == 2: line(x + w // 2, top - 5, x + w // 2, top - 1); P(x + w // 2 - 1, top - 4)       # antenna
    else:                                                                                       # billboard
        line(x + 4, top - 4, x + 4, top - 1); line(x + w - 5, top - 4, x + w - 5, top - 1)
        box(x + 2, top - 10, w - 4, 6)
        for xx in range(x + 4, x + w - 4, 3): P(xx, top - 8)
    x += w + random.randint(12, 24)
# construction crane: one mast, a jib, a load on a cable
cm = 4980; line(cm, 33, cm, G - 1, 2)
box(cm - 14, 31, 60, 3); line(cm + 36, 34, cm + 36, 40); box(cm + 31, 40, 11, 4)
for k in range(8): lamp(4430 + k * 120 + 40)

# ------------------------------------------------------------------ 7. harbor (5400-6200)
SECTIONS.append((5400, 'harbor'))
W0, W1 = 5470, 6150
for xx in range(W0, W1):                                               # water
    w = G + 1 + int(1.2 * math.sin(xx / 6)); gnd[xx] = 99
    dm.line([xx, w, xx, 63], fill=1)
    if (xx // 3) % 2 == 0: P(xx, w)
box(5400, G - 3, 70, 3, 1)                                            # dock
# gantry crane on the dock edge: fly under the beam between the legs
def harbor_crane(x):
    line(x, 40, x, G - 4, 2); box(x - 4, 36, 10, 5)                     # mast and cab
    line(x + 2, 37, x + 40, 35, 2)                                         # jib, nearly flat: fly over it
    line(x + 40, 37, x + 40, 43); box(x + 36, 43, 9, 3)                   # hook and spreader
harbor_crane(5420)
# container ship
sx = 5520; poly([(sx, G - 10), (sx + 150, G - 10), (sx + 140, G), (sx + 8, G)])
for k in range(10):
    for lvl in range(1 if k % 3 == 1 else 2):
        box(sx + 10 + k * 12, G - 16 - lvl * 6, 11, 6)
        for yy in range(G - 15 - lvl * 6, G - 11 - lvl * 6, 2): P(sx + 13 + k * 12, yy); P(sx + 17 + k * 12, yy)
box(sx + 128, G - 22, 14, 12); window(sx + 130, G - 20, 10, 4, True); line(sx + 135, G - 25, sx + 135, G - 22)
# second gantry crane out on a pier
pier = 5730; box(pier, G - 3, 60, 3, 1)
for xx in range(pier + 4, pier + 60, 10): line(xx, G, xx, 63)
harbor_crane(pier + 10)
# tug boat and buoys
tb = 5830; poly([(tb, G - 5), (tb + 26, G - 5), (tb + 22, G), (tb + 3, G)]); box(tb + 6, G - 11, 10, 6); window(tb + 8, G - 10, 6, 3, True); box(tb + 10, G - 15, 3, 4)
for bxx in (5900, 5960, 6040):
    poly([(bxx, G - 1), (bxx + 3, G - 9), (bxx + 6, G - 1)]); P(bxx + 3, G - 11)
# lighthouse on the far side
lh = 6100; box(6085, G - 4, 65, 4, 0); [gnd.__setitem__(xx, G - 4) for xx in range(6085, 6150)]
poly([(lh, G - 4), (lh + 4, G - 20), (lh + 10, G - 20), (lh + 14, G - 4)])
for yy in range(G - 16, G - 6, 5): di.line([lh + 2, yy, lh + 12, yy], fill=1)
box(lh + 3, G - 25, 9, 5); window(lh + 5, G - 24, 5, 3, True)

# ------------------------------------------------------------------ 8. mountain cave (6200-7000)
SECTIONS.append((6200, 'cave'))
for xx in range(6200, 7000):
    t = (xx - 6200) / 800
    gnd[xx] = int(G - 8 * math.sin(t * math.pi) - 4 * math.sin(t * 17))
    c = int(12 + 5 * math.sin(t * 21) + 2 * math.sin(t * 57))
    if t < 0.08: c = int(c * t / 0.08)
    if t > 0.92: c = int(c * (1 - t) / 0.08)
    if c > 0:
        dm.line([xx, 0, xx, c], fill=1); P(xx, c)
        for k in range(1, c, 4):
            if (xx * 5 + k * 7) % 13 == 0: P(xx, k)
for xx in range(6300, 6950, 67):                                       # crystals on the floor
    g = gnd[xx]; poly([(xx - 3, g), (xx - 1, g - 6), (xx + 1, g - 6), (xx + 3, g)])

# ------------------------------------------------------------------ 9. desert and Area 51 (7000-7808)
SECTIONS.append((7000, 'desert'))
for xx in range(7020, 7200, 55):
    box(xx, G - 13, 3, 13); box(xx - 4, G - 9, 3, 5); box(xx + 4, G - 11, 3, 6); di.line([xx - 3, G - 5, xx, G - 5], fill=1); di.line([xx + 3, G - 6, xx + 5, G - 6], fill=1)
fence(7260, 7380)
# hangar with a curved roof
hg = 7400; box(hg, G - 14, 60, 14); di.chord([hg, G - 26, hg + 59, G - 2], 180, 360, fill=0, outline=1); dm.chord([hg, G - 26, hg + 59, G - 2], 180, 360, fill=1)
for k in range(hg + 6, hg + 56, 8): di.line([k, G - 13, k, G - 1], fill=1)
# radar dish and watch tower
line(7490, G - 14, 7490, G - 1); di.arc([7480, G - 25, 7500, G - 10], 200, 340, fill=1); dm.arc([7480, G - 25, 7500, G - 10], 200, 340, fill=1); line(7490, G - 14, 7493, G - 19)
line(7520, G - 22, 7516, G - 1); line(7530, G - 22, 7534, G - 1); box(7514, G - 28, 22, 6); window(7517, G - 27, 16, 4, True)
FINISH = 7790                                                          # the mothership is drawn by the game, not here
for xx in range(7560, 7700, 37): P(xx, G - 1); P(xx + 1, G - 2)             # a few rocks under the mothership

# ------------------------------------------------------------------ extra detail in the quiet stretches
# tunnel: a handcar behind the train
hx = 1470; box(hx, G - 6, 14, 3); line(hx + 7, G - 11, hx + 7, G - 6); line(hx + 3, G - 11, hx + 11, G - 11)
for wx in (hx + 3, hx + 11): di.ellipse([wx - 2, G - 4, wx + 2, G], fill=0, outline=1); solid(wx - 2, G - 4, wx + 2, G)
# end of downtown: warehouses with roll-up doors, stacked containers, a forklift
for (wx0, ww, wh) in ((5050, 44, 16), (5110, 36, 13)):
    box(wx0, G - wh, ww, wh); dither_poly([(wx0 - 2, G - wh), (wx0 + ww // 2, G - wh - 5), (wx0 + ww + 1, G - wh)])
    for dx in range(wx0 + 4, wx0 + ww - 10, 14):
        di.rectangle([dx, G - 9, dx + 9, G - 1], fill=0, outline=1)
        for yy in range(G - 8, G - 1, 2): di.line([dx + 1, yy, dx + 8, yy], fill=1)
for k, (cx_, lv) in enumerate(((5170, 2), (5184, 1), (5198, 2), (5240, 1), (5254, 2))):
    for l in range(lv):
        box(cx_, G - 6 - l * 6, 13, 6)
        for xx in range(cx_ + 2, cx_ + 12, 2): P(xx, G - 4 - l * 6)
fx = 5290; box(fx, G - 8, 10, 5); line(fx + 2, G - 13, fx + 2, G - 8); line(fx + 2, G - 13, fx + 7, G - 13)
line(fx + 10, G - 12, fx + 10, G - 3); line(fx + 10, G - 3, fx + 15, G - 3)
for wx in (fx + 2, fx + 8): di.ellipse([wx - 2, G - 4, wx + 2, G], fill=0, outline=1); solid(wx - 2, G - 4, wx + 2, G)
# harbor: a sailboat, a rowboat and a gull on a post between the pier and the lighthouse
sb = 5935
poly([(sb, G - 4), (sb + 24, G - 4), (sb + 20, G), (sb + 3, G)])
line(sb + 11, G - 24, sb + 11, G - 4)
poly([(sb + 12, G - 23), (sb + 12, G - 6), (sb + 22, G - 6)])
poly([(sb + 10, G - 20), (sb + 10, G - 6), (sb + 3, G - 6)])
rb = 6010; poly([(rb, G - 3), (rb + 14, G - 3), (rb + 11, G), (rb + 3, G)]); line(rb + 4, G - 6, rb + 9, G - 3)
gp = 6060; line(gp, G - 10, gp, G - 1); box(gp - 1, G - 11, 3, 1, 1); P(gp - 2, G - 13); P(gp - 1, G - 12); P(gp + 1, G - 12); P(gp + 2, G - 13)
# desert: a road, rocks, a broken-down truck with its hood up, a tumbleweed, and a KEEP OUT sign
for xx in range(7000, 7600, 8): P(xx, G + 3); P(xx + 1, G + 3); P(xx + 2, G + 3)
for (rx_, rw, rh) in ((7045, 14, 6), (7140, 20, 9), (7210, 12, 5)):
    poly([(rx_, G - 1), (rx_ + 3, G - rh), (rx_ + rw - 4, G - rh - 1), (rx_ + rw, G - 1)])
    for k in range(3): P(rx_ + 4 + k * 3, G - rh + 3)
tk = 7093; box(tk, G - 10, 18, 7); box(tk + 18, G - 8, 8, 5); line(tk + 18, G - 8, tk + 23, G - 13)
window(tk + 2, G - 9, 5, 3, False)
for wx in (tk + 4, tk + 21): di.ellipse([wx - 3, G - 5, wx + 3, G], fill=0, outline=1); solid(wx - 3, G - 5, wx + 3, G)
for k in range(3): P(tk + 24 + k, G - 15 - k * 2)
tw = 7180; di.ellipse([tw, G - 7, tw + 7, G - 1], fill=0, outline=1); dm.ellipse([tw, G - 7, tw + 7, G - 1], fill=1)
di.line([tw + 1, G - 5, tw + 6, G - 3], fill=1); di.line([tw + 2, G - 2, tw + 5, G - 6], fill=1)
sg = 7238; line(sg + 3, G - 10, sg + 3, G - 1); line(sg + 15, G - 10, sg + 15, G - 1)
di.rectangle([sg, G - 22, sg + 18, G - 10], fill=1); dm.rectangle([sg, G - 22, sg + 18, G - 10], fill=1)
KEEP = {'K':[31,4,27],'E':[31,21,17],'P':[31,5,2],'O':[14,17,14],'U':[15,16,15],'T':[1,31,1]}
cx_ = sg + 2
for ch in "KEEP":
    for i, b in enumerate(KEEP[ch]):
        for j in range(5):
            if b >> j & 1: P(cx_ + i, G - 21 + j, 0)
    cx_ += 4
cx_ = sg + 4
for ch in "OUT":
    for i, b in enumerate(KEEP[ch]):
        for j in range(5):
            if b >> j & 1: P(cx_ + i, G - 16 + j, 0)
    cx_ += 4

# ------------------------------------------------------------------ ground
for xx in range(LW):
    g = gnd[xx]
    if g >= 64: continue
    dm.line([xx, g, xx, 63], fill=1); P(xx, g)
    if g < 62 and xx % 9 == 3: P(xx, g + 2)
    if g < 61 and xx % 9 == 7: P(xx, g + 4)
    if xx > 0 and gnd[xx - 1] < 64 and abs(gnd[xx - 1] - g) > 1: di.line([xx, min(g, gnd[xx - 1]), xx, max(g, gnd[xx - 1])], fill=1)

msk = ImageChops.logical_or(msk, img)                                   # anything drawn can kill you
img.save('level_img.png'); msk.save('level_msk.png')
def pages(im):
    px = im.load(); out = bytearray()
    for p in range(8):
        for x in range(LW):
            b = 0
            for k in range(8):
                if px[x, p * 8 + k]: b |= 1 << k
            out.append(b)
    return out
a, b = pages(img), pages(msk)                                         # stored as image/mask byte pairs, row by row
inter = bytearray(len(a) * 2); inter[0::2] = a; inter[1::2] = b
open('level.bin', 'wb').write(inter)
open('sections.txt', 'w').write('\n'.join('%d %s' % s for s in SECTIONS))
print('LW', LW, 'FINISH', FINISH, SECTIONS)
