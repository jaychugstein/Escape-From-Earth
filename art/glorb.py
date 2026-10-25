import numpy as np, math
from PIL import Image
W,H=128,64
S=np.zeros((H,W),np.uint8)
def px(x,y,v=1):
    if 0<=x<W and 0<=y<H: S[y,x]=v
# ---- Glorb's head: big dome tapering to a small chin
cx=31
def inside(x,y):
    if y<34:
        return ((x-cx)/27.0)**2+((y-27)/24.0)**2<=1
    # lower face narrows to the chin
    t=min(1.0,(y-34)/(62-34))
    hw=27*math.sqrt(max(0,1-((34-27)/24.0)**2))*(1-t)**0.8+2*(t<1)
    return abs(x-cx)<=hw and y<=62
for y in range(H):
    for x in range(64):
        if inside(x,y):
            S[y,x]=1
# shading: lit from the upper left, ordered dither for smooth tones
B4=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
for y in range(H):
    for x in range(64):
        if S[y,x]:
            nx=(x-cx)/27.0; ny=(min(y,40)-27)/24.0
            nz=math.sqrt(max(0.0,1-nx*nx-ny*ny))
            I=0.40+0.95*max(0.0,-0.55*nx-0.45*ny+0.70*nz)
            if y>40: I-= (y-40)/60.0
            S[y,x]=1 if I>(B4[y%4][x%4]+0.5)/16 else 0
# black outline ring so the head reads cleanly
from scipy.ndimage import binary_erosion
mask=np.zeros((H,W),bool)
for y in range(H):
    for x in range(64): mask[y,x]=inside(x,y)
edge=mask & ~binary_erosion(mask)
for y,x in zip(*np.where(edge)): S[y,x]=1
# ---- eyes: huge slanted almonds
def eye(ex,ey,rx,ry,ang,flip):
    a=math.radians(ang)
    for y in range(ey-12,ey+13):
        for x in range(ex-14,ex+15):
            dx,dy=x-ex,y-ey
            u= dx*math.cos(a)+dy*math.sin(a)
            v=-dx*math.sin(a)+dy*math.cos(a)
            # almond: pointy at the outer end
            k = 1 - (0.35*u/rx if (u*flip)>0 else 0)
            if (u/rx)**2+(v/(ry*max(k,0.3)))**2<=1: px(x,y,0)
eye(19,33,11,6,28,-1)
eye(43,33,11,6,-28,1)
from scipy.ndimage import binary_dilation as _bd
S2=S.copy(); S[:]=1
eye(19,33,11,6,28,-1); eye(43,33,11,6,-28,1)
eyes=(S==0); S[:]=S2
ring=_bd(eyes,iterations=1)&~eyes
S[ring&mask]=1
# glints
for (x,y) in [(15,30),(16,30),(15,31),(39,29),(40,29),(40,30)]: px(x,y,1)
px(22,35,1); px(46,35,1)
# brow lines
for i in range(8): px(12+i,24-i//3,0); px(43+i,22+i//3,0)
# nostrils + smirk (on a light patch so they show)
for yy in range(41,57):                                          # soft round light patch (no hard edges)
    for xx in range(21,42):
        d=((xx-31)/10.0)**2+((yy-49)/7.0)**2
        if mask[yy,xx] and d<1:
            if d<0.3: on=True
            elif d<0.55: on=(xx+yy)%3!=0
            elif d<0.75: on=(xx+yy)%2==0
            else: on=(xx+yy)%4==0 and yy%2==0
            if on: px(xx,yy,1)
px(29,45,0); px(33,45,0); px(29,46,0); px(33,46,0)
for i in range(10):
    yy=52-(1 if i>6 else 0)-(1 if i>8 else 0); px(26+i,yy,0); px(26+i,yy+1,1)
px(25,51,0)
# antenna-ish wrinkle on the dome
for i in range(6): px(28+i,10+(i%2),0)
# ---- a little # bruise on his forehead: he got bonked
bx,by=43,11
for y in range(by-2,by+9):                                       # round light patch so the mark reads
    for x in range(bx-2,bx+9):
        if (x-bx-3)**2+(y-by-3)**2<=22: px(x,y,1)
for k in (2,5):
    for i in range(7): px(bx+k,by+i,0); px(bx+i,by+k,0)            # the # mark
# ---- speech bubble on the right
bx0,by0,bx1,by1=66,2,126,52
for x in range(bx0+2,bx1-1): px(x,by0); px(x,by1)
for y in range(by0+2,by1-1): px(bx0,y); px(bx1,y)
px(bx0+1,by0+1);px(bx1-1,by0+1);px(bx0+1,by1-1);px(bx1-1,by1-1)
# tail pointing at his mouth
for i in range(9): px(bx0-i,40+i//2); px(bx0-i+1,44)
for y in range(41,45): px(bx0,y,0)
for i in range(1,8): 
    for y in range(41+i//2,44): px(bx0-i+1,y,0)
TINY={}
digs=[[31,17,31],[0,31,0],[29,21,23],[21,21,31],[7,4,31],[23,21,29],[31,21,29],[1,1,31],[31,21,31],[23,21,31]]
let=[[30,5,30],[31,21,10],[14,17,17],[31,17,14],[31,21,17],[31,5,1],[14,17,29],[31,4,31],[17,31,17],[8,16,15],[31,4,27],[31,16,16],[31,2,4,2,31],[31,1,30],[14,17,14],[31,5,2],[14,17,30],[31,5,26],[18,21,9],[1,31,1],[15,16,15],[7,24,7],[31,8,4,8,31],[27,4,27],[3,28,3],[25,21,19]]
for i,g in enumerate(digs): TINY[str(i)]=g
for i,g in enumerate(let): TINY[chr(65+i)]=g
TINY[' ']=[0,0]; TINY[',']=[16,8]; TINY['.']=[16]; TINY["'"]=[3]; TINY['-']=[4,4,4]
def tiny(x,y,s):
    for ch in s:
        g=TINY[ch]
        for i,b in enumerate(g):
            for j in range(5):
                if b>>j&1: px(x+i,y+j)
        x+=len(g)+1
    return x
def width(s): return sum(len(TINY[c])+1 for c in s)-1
tiny(122-width("- GLORB"),46,"- GLORB")
Image.fromarray(S*255).resize((512,256),0).save('glorb_4x.png')
np.save('glorb.npy',S)
