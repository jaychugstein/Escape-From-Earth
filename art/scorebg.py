# Background for the end screens: a framed panel with stars round the edge and a saucer either side of the title.
import random
from PIL import Image
from sprites import SPR
W, H = 128, 64
im = Image.new('1', (W, H), 0); P = lambda x, y, v=1: im.putpixel((x, y), v) if 0 <= x < W and 0 <= y < H else None
for x in range(2, W - 2): P(x, 0); P(x, H - 1)                 # double frame with rounded corners
for y in range(2, H - 2): P(0, y); P(W - 1, y)
P(1, 1); P(W - 2, 1); P(1, H - 2); P(W - 2, H - 2)
for x in range(4, W - 4, 2): P(x, 2)                             # dotted inner frame (top only, text sits low)
for y in range(4, H - 4, 2): P(2, y); P(W - 3, y + 1)
for (cx, cy) in ((5, H - 6), (W - 6, H - 6)):   # bolts in the corners
    for d in (-1, 0, 1): P(cx + d, cy); P(cx, cy + d)
ufo = SPR['ufo'][0]
for (ox, oy) in ((5, 3), (W - 25, 3)):                          # little saucers flanking the title
    for j, r in enumerate(ufo):
        for i, c in enumerate(r):
            if c == '#': P(ox + i, oy + j)
random.seed(9)
for k in range(10):                                           # a few stars just inside the frame
    P(random.choice([4, 5, W - 6, W - 5]), random.randrange(12, H - 12))
out = bytes(sum(im.getpixel((x, p * 8 + k)) << k for k in range(8)) for p in range(8) for x in range(W))
open('scorebg.bin', 'wb').write(out)
im.resize((W * 4, H * 4), 0).save('preview/scorebg.png')
