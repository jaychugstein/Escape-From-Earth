# Saucer drawn at 64 angles (2 light frames each) for rocket-style flying. Appended to the FX data.
import math, sys, os
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprites import SPR
def frame_bytes(frame, w, h):                 # FX masked-bitmap bytes: per 8-row page, per column: picture, mask
    pages = (h + 7) // 8; out = []
    for p in range(pages):
        for x in range(w):
            img = msk = 0
            for b in range(8):
                y = p * 8 + b
                if y >= h: continue
                r = frame[y]; c = r[x] if x < len(r) else '.'
                if c in '#o': msk |= 1 << b
                if c == '#': img |= 1 << b
            out += [img, msk]
    return out
N, S = 64, 24
src = SPR['ufo']; SW, SH = 20, 9; cx, cy = 9.5, 4.5
frames = []
from ufo_vec import frame as vframe
for a in range(N):
    for f in src:
        out = vframe(a * 360.0 / N, S, src.index(f))                   # drawn from the same shapes at every angle, so it never changes shape
        frames.append(out)
blob = bytes([0, S, 0, S]) + b''.join(bytes(frame_bytes(fr, S, S)) for fr in frames)
open('ufo_rot.bin', 'wb').write(blob)              # packed into the FX data by fxpack.py
# preview
im = Image.new('L', (16 * 26, 4 * 26), 60)
for i in range(64):
    fr = frames[i * 2]
    for y, r in enumerate(fr):
        for x, c in enumerate(r):
            if c != '.': im.putpixel(((i % 16) * 26 + x, (i // 16) * 26 + y), 255 if c == '#' else 0)
im.resize((im.width * 3, im.height * 3), 0).save('preview/ufo_rot.png')
print('ufo_rot.bin', len(blob))
