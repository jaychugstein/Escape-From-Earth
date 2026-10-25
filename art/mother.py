# The mothership at the end of the course: the left part of a giant saucer, with an open hangar bay.
# Saved as an FX masked bitmap (100 x 64). The game slides it up when it leaves.
import math
from PIL import Image, ImageDraw
W, H = 100, 64
G = 57                                    # ground line in the level
img = Image.new('1', (W, H), 0)           # white pixels
msk = Image.new('1', (W, H), 0)           # solid (drawn) pixels
di, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
def P(x, y, v=1):
    if 0 <= x < W and 0 <= y < H: img.putpixel((x, y), v)
def M(x, y):
    if 0 <= x < W and 0 <= y < H: msk.putpixel((x, y), 1)
def ell_fill(cx, cy, rx, ry, y0, y1, pattern=None, edge=True):
    """fill the part of an ellipse between rows y0..y1; pattern(x,y) decides white pixels inside"""
    for y in range(max(0, y0), min(H, y1 + 1)):
        t = (y - cy) / ry
        if abs(t) > 1: continue
        hw = rx * math.sqrt(1 - t * t)
        xa, xb = int(round(cx - hw)), int(round(cx + hw))
        for x in range(max(0, xa), min(W, xb + 1)):
            M(x, y)
            if pattern and pattern(x, y): P(x, y)
        if edge: P(xa, y)
BAND_T, BAND_B = 12, 36                   # the thick rim
BAY_L, BAY_R, BAY_T, BAY_B = 12, 50, 15, 33
NOSE = 4
# --- upper hull (curves up from the rim to the dome)
ell_fill(118, BAND_T, 112, 9, BAND_T - 9, BAND_T, lambda x, y: y % 3 == 0 and x % 2 == 0 and y < BAND_T - 1)
for x in range(W):                                        # hull outline
    t = (x - 118) / 112
    if abs(t) <= 1: P(x, int(round(BAND_T - 9 * math.sqrt(1 - t * t))))
# --- dome with lit portholes
ell_fill(104, BAND_T - 7, 36, 15, -20, BAND_T - 8, lambda x, y: False)
for x in range(W):
    t = (x - 104) / 36
    if abs(t) <= 1: P(x, int(round(BAND_T - 7 - 15 * math.sqrt(1 - t * t))))
for k, x in enumerate(range(74, 100, 7)):                  # portholes
    y = -1 + int(abs(x - 92) * 0.12)
    di.ellipse([x, y, x + 3, y + 3], outline=1)
    if k % 2: P(x + 1, y + 1); P(x + 2, y + 2)
# --- the rim band: rounded nose, panel seams, row of lights (lights animated by the game)
for y in range(BAND_T, BAND_B + 1):
    t = (y - (BAND_T + BAND_B) / 2) / ((BAND_B - BAND_T) / 2)
    nose = int(round(NOSE + 6 * (1 - math.sqrt(max(0, 1 - t * t)))))   # rounded leading edge
    for x in range(nose, W): M(x, y)
    P(nose, y)
di.line([NOSE + 2, BAND_T, W, BAND_T], fill=1); di.line([NOSE + 2, BAND_B, W, BAND_B], fill=1)
di.line([BAY_R + 4, BAND_T + 3, W, BAND_T + 3], fill=1); di.line([BAY_R + 4, BAND_B - 3, W, BAND_B - 3], fill=1)
for x in range(BAY_R + 10, W, 12):                        # panel seams
    di.line([x, BAND_T + 4, x, BAND_B - 4], fill=1)
    for y in range(BAND_T + 6, BAND_B - 5, 3): P(x + 4, y)
# --- lower hull, darker (sparse dots), with belly lights
ell_fill(118, BAND_B, 108, 7, BAND_B, BAND_B + 7, lambda x, y: (x * 3 + y * 5) % 9 == 0)
for x in range(W):
    t = (x - 118) / 108
    if abs(t) <= 1: P(x, int(round(BAND_B + 7 * math.sqrt(1 - t * t))))
# --- landing legs: thick, angled, with feet on the ground
for (lx, fx) in ((44, 34), (80, 76)):
    top = BAND_B + 4
    for w in range(-3, 4):
        di.line([lx + w, top, fx + w, G - 3], fill=1 if abs(w) == 3 else 0); dm.line([lx + w, top, fx + w, G - 3], fill=1)
    di.line([lx - 3, top + 4, lx + 3, top + 4], fill=1)                         # joint collar
    di.rectangle([fx - 6, G - 3, fx + 6, G - 1], fill=1); dm.rectangle([fx - 6, G - 3, fx + 6, G - 1], fill=1)
    di.rectangle([fx - 3, G - 5, fx + 3, G - 4], fill=1); dm.rectangle([fx - 3, G - 5, fx + 3, G - 4], fill=1)
# --- the hangar bay: frame with hazard stripes, dark inside, floor lines running to the back wall
for y in range(BAY_T, BAY_B + 1):                          # the bay is open right through the nose
    for x in range(0, BAY_R + 1):
        img.putpixel((x, y), 0)
        if x < BAY_L - 2: msk.putpixel((x, y), 0)
for x in range(NOSE + 3, BAY_R + 3):                       # striped top and bottom edges
    for d in (1, 2):
        v = 1 if ((x + d) // 2) % 2 == 0 else 0
        P(x, BAY_T - d, v); M(x, BAY_T - d); P(x, BAY_B + d, v); M(x, BAY_B + d)
di.line([NOSE + 3, BAY_T - 3, BAY_R + 2, BAY_T - 3], fill=1); di.line([NOSE + 3, BAY_B + 3, BAY_R + 2, BAY_B + 3], fill=1)
di.line([BAY_R + 1, BAY_T - 3, BAY_R + 1, BAY_B + 3], fill=1)                    # back wall
for y in range(BAY_T + 2, BAY_B - 1, 3): P(BAY_R - 1, y)
for k in range(4):                                          # floor and ceiling guide lines in perspective
    xs = BAY_L + 4 + k * 9
    P(xs, BAY_B - 1); P(xs + 1, BAY_B - 1); P(xs, BAY_T + 1); P(xs + 1, BAY_T + 1)
# --- widen the picture to the left to make room for the open jaw
OX = 30; W2 = W + OX
img2 = Image.new('1', (W2, H), 0); msk2 = Image.new('1', (W2, H), 0)
img2.paste(img, (OX, 0)); msk2.paste(msk, (OX, 0))
img, msk, W = img2, msk2, W2
di, dm = ImageDraw.Draw(img), ImageDraw.Draw(msk)
BAY_L += OX; BAY_R += OX; NOSE += OX
img.save('mother.png'); msk.save('mother_mask.png')
# FX masked bitmap: w, h (16-bit), then per 8-row page, per column: picture byte, mask byte
out = bytearray([0, W, 0, H])
for p in range(H // 8):
    for x in range(W):
        a = b = 0
        for k in range(8):
            y = p * 8 + k
            if img.getpixel((x, y)): a |= 1 << k
            if msk.getpixel((x, y)): b |= 1 << k
        out += bytes([a, b])
open('mother.bin', 'wb').write(out)
# preview on a night background
pv = Image.new('L', (W + 40, H), 0)
import random; random.seed(2)
for k in range(40): pv.putpixel((random.randrange(W + 40), random.randrange(G)), 255)
for x in range(W + 40): pv.putpixel((x, G), 255)
for y in range(H):
    for x in range(W):
        if msk.getpixel((x, y)): pv.putpixel((x + 40, y), 255 if img.getpixel((x, y)) else 0)
pv.resize((pv.width * 5, pv.height * 5), 0).save('preview/mother_preview.png')
print('BAY', BAY_L, BAY_R, BAY_T, BAY_B, 'bytes', len(out))
