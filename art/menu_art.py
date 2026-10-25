# Sound screen pictures: SOUND ON / SOUND OFF, two frames each (the saucer bobs, notes bounce).
import numpy as np, random, math, sys
from PIL import Image
from font import FONT
from sprites import SPR
W, H = 128, 64
def render(on, t):
    S = np.zeros((H, W), np.uint8)
    def px(x, y, v=1):
        if 0 <= x < W and 0 <= y < H: S[y, x] = v
    random.seed(3)
    for k in range(40):                                        # stars
        x, y = random.randrange(W), random.randrange(H - 8)
        if (k + t) % 7: px(x, y)
    def big(txt, y, wob=True, italic=True):
        wid = sum(11 if c != ' ' else 5 for c in txt) - 1
        x0 = (W - wid) // 2 - 1
        def draw(xo, yo, v, halo=False):
            x = x0
            for ci, ch in enumerate(txt):
                wy = ((ci + t) % 2) if wob else 0          # every letter bobs, neighbours opposite ways
                g = ord(ch) - 32
                for i in range(5):
                    b = FONT[g * 5 + i]
                    for j in range(7):
                        if b >> j & 1:
                            for dy in range(2):
                                yy = y + wy + j * 2 + dy; sl = (14 - (j * 2 + dy)) // 6 if italic else 0
                                for dx in range(2):
                                    if halo:
                                        for hx in (-1, 0, 1):
                                            for hy in (-1, 0, 1): px(x + i * 2 + dx + sl + xo + hx, yy + yo + hy, 0)
                                    else: px(x + i * 2 + dx + sl + xo, yy + yo, v)
                x += 11 if ch != ' ' else 5
        # dithered drop shadow, black halo, white letters
        sh = np.zeros_like(S); keep = S.copy(); S[:] = 0; draw(2, 2, 1); sh = S.copy(); S[:] = keep
        for yy in range(H):
            for xx in range(W):
                if sh[yy, xx] and (xx + yy) % 2 == 0: S[yy, xx] = 1
        draw(0, 0, 0, halo=True); draw(0, 0, 1)
    big("SOUND", 1)
    # the saucer, twice as big, bobbing
    ufo = SPR['ufo'][t % 2]; ux, uy = 44, 20 + (t % 2)
    for j, r in enumerate(ufo):
        for i, c in enumerate(r):
            if c != '.':
                for dx in range(2):
                    for dy in range(2): px(ux + i * 2 + dx, uy + j * 2 + dy, 1 if c == '#' else 0)
    note = ["...##..", "...#.#.", "...#..#", "...#...", "...#...", ".###...", "####...", ".##...."]
    def drawnote(x, y):
        for j, r in enumerate(note):
            for i, c in enumerate(r):
                if c == '#': px(x + i, y + j)
    if on:
        for (x, y, ph) in ((18, 20, 0), (30, 30, 1), (96, 22, 1), (108, 31, 0)):
            drawnote(x, y - 2 * ((t + ph) % 2))
    else:
        for (x, y) in ((22, 26), (98, 26)):                    # sleepy Zs
            for k, (dx, dy, s) in enumerate(((0, 6, 4), (6, 0, 3))):
                yy = y + dy - (t % 2); xx = x + dx
                for i in range(s): px(xx + i, yy); px(xx + i, yy + s); px(xx + s - 1 - i, yy + i)
    big("< ON >" if on else "< OFF >", 40, wob=False, italic=False)
    return S
frames = [render(on, t) for on in (1, 0) for t in (0, 1)]
out = b''.join(bytes(sum(int(f[p * 8 + k, x]) << k for k in range(8)) for p in range(8) for x in range(W)) for f in frames)
open('menu.bin', 'wb').write(out)
strip = np.concatenate([np.pad(f, ((1, 1), (1, 1)), constant_values=0) for f in frames], 1)
Image.fromarray(strip * 255).resize((strip.shape[1] * 3, strip.shape[0] * 3), 0).save('preview/menu_frames.png')
