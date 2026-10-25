import numpy as np, random
from PIL import Image
from font import FONT
W,H=128,64
S=np.zeros((H,W),np.uint8)
def px(x,y,v=1):
    if 0<=x<W and 0<=y<H: S[y,x]=v
def ell(cx,cy,rx,ry,fill=None,outline=None,half=None):
    for y in range(int(cy-ry)-1,int(cy+ry)+2):
        for x in range(int(cx-rx)-1,int(cx+rx)+2):
            d=((x-cx)/rx)**2+((y-cy)/ry)**2
            if half=='top' and y>cy: continue
            if d<=1:
                if outline is not None and d>(1-2.2/min(rx,ry)): px(x,y,outline)
                elif fill is not None: px(x,y,fill)
def sprite(rows,x0,y0):
    for j,r in enumerate(rows):
        for i,c in enumerate(r):
            if c=='#': px(x0+i,y0+j,1)
            elif c=='o': px(x0+i,y0+j,0)
def render(t):
    S[:]=0
    random.seed(7)
    # stars
    for k in range(45):                       # a few stars wink out now and then, at random
        x,y=random.randrange(W),random.randrange(1,56); ph=random.randrange(8); blinks=random.random()<0.35
        if not (blinks and t==ph): px(x,y)
    for (x,y),ph in zip([(8,22),(118,40),(20,44),(104,21),(12,6),(112,9)],[5,2,7,0,3,6]):
        px(x,y)                                # bright stars: each one sparkles briefly at its own moment
        if t==ph: px(x-1,y);px(x+1,y);px(x,y-1);px(x,y+1)
    # moon
    ell(114,24,5,5,fill=1); ell(112,22,4,4,fill=0)
    bob=8+[0,0,1,2,2,2,1,0][t]   # gentle hover, under the two-line title
    # UFO
    ell(64,29+bob,13,13,fill=0,half='top'); ell(64,29+bob,13,13,outline=1,half='top')  # glass dome
    px(56,22+bob);px(56,21+bob);px(57,20+bob)                                            # glint
    alien=[
    "...#####...",
    "..#######..",
    ".#########.",
    "###########",
    "#oo#####oo#",
    "#ooo###ooo#",
    ".#oo###oo#.",
    "..#######..",
    "...#####...",
    "....###....",
    "..#######..",
    ]
    sprite(alien,59,18+bob)
    ell(64,33+bob,30,6,fill=1)                                                   # saucer
    for x in range(35,94): px(x,31+bob,0)                                         # panel line
    for x in range(39,90,6): px(x,33+bob,0); px(x+1,33+bob,0); px(x,34+bob,0); px(x+1,34+bob,0)   # windows
    for x in range(35,94): px(x,36+bob,0)
    ell(64,38+bob,16,3,fill=1)                                                   # underside
    for x in range(51+t%4,78,4): px(x,39+bob,0)                                       # lights

    # ground: hills with a barn and fence
    for x in range(W):
        h=57+int(2*np.sin(x/9.0)+1.5*np.sin(x/4.3))
        for y in range(h,H): px(x,y,0)
        px(x,h,1)
    barn=[
    "....##....",
    "..##..##..",
    ".#......#.",
    "#.#....#.#",
    "#..#..#..#",
    "#...##...#",
    "#..#..#..#",
    "#.#....#.#",
    ]
    barn=[
".......####.......",
".....##oooo##.....",
"...##oooooooo##...",
"..#oooo####oooo#..",
".#ooooo#oo#ooooo#.",
"#oooooo####oooooo#",
"##################",
"#ooo##########ooo#",
"#ooo##oooooo##ooo#",
"#ooo#o#oooo#o#ooo#",
"#ooo#oo#oo#oo#ooo#",
"#ooo#ooo##ooo#ooo#",
"#ooo#oo#oo#oo#ooo#",
"#ooo#o#oooo#o#ooo#",
"##################",
]
    sprite(barn,2,42)
    for x in range(98,124,5):
        for y in range(52,57): px(x,y)
    for x in range(98,122): px(x,53); px(x,55)
    # title: italic 2x letters with a dithered drop shadow
    def bigtext(txt,x,y,v):
        for ci,ch in enumerate(txt):
            wy=int(round(np.sin(2*np.pi*t/8+ci*0.7)))
            g=ord(ch)-32
            for i in range(5):
                b=FONT[g*5+i]
                for j in range(7):
                    if b>>j&1:
                        for dy in range(2):
                            yy=y+wy+j*2+dy; sl=(14-(j*2+dy))//6
                            for dx in range(2): px(x+i*2+dx+sl,yy,v)
            x+=11 if ch!=' ' else 5
    txt="ESCAPE"; tx=30
    # shadow
    tmp=S.copy(); bigtext(txt,tx+2,3,1); sh=S.copy(); S[:]=tmp
    for y in range(H):
        for x in range(W):
            if sh[y,x] and not tmp[y,x] and (x+y)%2==0: S[y,x]=1
    # black knockout then letters
    S2=S.copy(); bigtext(txt,tx,1,1); L=(S2!=S)|(S2==1)&(S==0)
    let=np.zeros_like(S); S[:]=0; 
    S[:]=tmp
    for y in range(H):
        for x in range(W):
            if sh[y,x] and not tmp[y,x] and (x+y)%2==0: S[y,x]=1
    mask=np.zeros_like(S); tmpS=S.copy(); S[:]=0; bigtext(txt,tx,1,1); mask=S.copy(); S[:]=tmpS
    from scipy.ndimage import binary_dilation
    halo=binary_dilation(mask,iterations=1)
    S[halo]=0; S[mask==1]=1
    # second line, smaller: FROM EARTH (letters bob a little)
    sx=64-(10*6-1)//2
    for ci,ch in enumerate("FROM EARTH"):
        wy=int(round(0.6*np.sin(2*np.pi*t/8+ci*0.7+1)))
        if ch!=' ':
            g=ord(ch)-32
            for i in range(5):
                b=FONT[g*5+i]
                for j in range(7):
                    for dx in (-1,0,1):
                        for dy in (-1,0,1): pass
            for i in range(-1,6):
                for j in range(-1,8): px(sx+i,19+wy+j,0)
            for i in range(5):
                b=FONT[g*5+i]
                for j in range(7):
                    if b>>j&1: px(sx+i,19+wy+j,1)
        sx+=6
    return S.copy()

frames=[render(t) for t in range(8)]
np.save('title.npy',frames[0])
for t,f in enumerate(frames): np.save('title_f%d.npy'%t,f)
Image.fromarray(frames[0]*255).resize((512,256),0).save('title_4x.png')
strip=np.concatenate([np.pad(f,((1,1),(1,1)),constant_values=0) for f in frames[:4]],1)
Image.fromarray(strip*255).resize((strip.shape[1]*3,strip.shape[0]*3),0).save('/home/claude/ufo/title_frames.png')
