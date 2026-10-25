# Draws the saucer at any angle from simple shapes: a lens-shaped hull, a round glass dome and a row of lights.
# The dome is a circle, so it looks the same at every tilt instead of turning pointy or sliding around.
import math
A, BT, BB = 10.0, 2.7, 2.9          # hull: half length, thickness above / below the middle
DR, DI, DC = 3.4, 2.1, -1.9         # dome: outer radius, glass radius, centre (above the middle)
LV = 1.2                            # the row of lights, just below the middle
def frame(deg, S=24, ph=0, ss=8):
    th = math.radians(deg); co, si = math.cos(th), math.sin(th); C = S / 2
    def hull(u, v): return (u / A) ** 2 + (v / (BT if v < 0 else BB)) ** 2 <= 1
    def dome(u, v, r): return u * u + (v - DC) ** 2 <= r * r and v <= DC + 0.3
    g = [['.'] * S for _ in range(S)]
    for y in range(S):
        for x in range(S):
            n = gl = 0
            for sy in range(ss):
                for sx in range(ss):
                    dx = x + (sx + .5) / ss - C; dy = y + (sy + .5) / ss - C
                    u = dx * co + dy * si; v = -dx * si + dy * co
                    if hull(u, v) or dome(u, v, DR): n += 1
                    if dome(u, v, DI): gl += 1
            if n > ss * ss * 0.42: g[y][x] = 'g' if gl > ss * ss * 0.5 else '#'
    def solid(x, y): return 0 <= x < S and 0 <= y < S and g[y][x] != '.'
    for y in range(S):                                # the glass always keeps a white rim around it
        for x in range(S):
            if g[y][x] == 'g':
                g[y][x] = 'o' if all(solid(x + a, y + b) for a in (-1, 0, 1) for b in (-1, 0, 1)) else '#'
    for k in range(-4, 4):                            # lights: one dot every 2 pixels, shifted by one on the other frame
        u = 2 * k + 0.5 + ph
        if abs(u) > 7: continue
        px, py = u * co - LV * si + C, u * si + LV * co + C
        X, Y = int(math.floor(px + 1e-6)), int(math.floor(py + 1e-6))
        if all(solid(X + a, Y + b) for a, b in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))): g[Y][X] = 'o'
    return [''.join(r) for r in g]
