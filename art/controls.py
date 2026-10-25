import numpy as np
from PIL import Image
W,H=128,64
S=np.zeros((H,W),np.uint8)
def px(x,y,v=1):
    if 0<=x<W and 0<=y<H: S[y,x]=v
def rect(x,y,w,h,v=1,fill=False):
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            if fill or yy in (y,y+h-1) or xx in (x,x+w-1): px(xx,yy,v)
def circ(cx,cy,r,fill=False,v=1):
    for y in range(cy-r-1,cy+r+2):
        for x in range(cx-r-1,cx+r+2):
            d=((x-cx)**2+(y-cy)**2)**0.5
            if (fill and d<=r+0.3) or (not fill and abs(d-r)<0.6): px(x,y,v)
TINY={}
digs=[[31,17,31],[0,31,0],[29,21,23],[21,21,31],[7,4,31],[23,21,29],[31,21,29],[1,1,31],[31,21,31],[23,21,31]]
let=[[30,5,30],[31,21,10],[14,17,17],[31,17,14],[31,21,17],[31,5,1],[14,17,29],[31,4,31],[17,31,17],[8,16,15],[31,4,27],[31,16,16],[31,2,31],[31,1,30],[14,17,14],[31,5,2],[14,17,30],[31,5,26],[18,21,9],[1,31,1],[15,16,15],[7,24,7],[31,8,31],[27,4,27],[3,28,3],[25,21,19]]
for i,g in enumerate(digs): TINY[str(i)]=g
for i,g in enumerate(let): TINY[chr(65+i)]=g
TINY[' ']=[0,0,0]; TINY['/']=[24,4,3]
def tiny(x,y,s,v=1):
    for ch in s:
        for i,b in enumerate(TINY[ch]):
            for j in range(5):
                if b>>j&1: px(x+i,y+j,v)
        x+=4
    return x
# board, modelled on the POOM: case frame, two USB-C ports, wide screen, big module, SD slot,
# d-pad in a clear ring, two round buttons inside a pill outline, screws in the corners
bx,by,bw,bh=28,9,72,48
def rrect(x,y,w,h,r=2,v=1):
    for xx in range(x+r,x+w-r): px(xx,y,v); px(xx,y+h-1,v)
    for yy in range(y+r,y+h-r): px(x,yy,v); px(x+w-1,yy,v)
    for k in range(r):                      # little diagonal corners
        px(x+r-1-k,y+1+k,v); px(x+w-r+k,y+1+k,v); px(x+r-1-k,y+h-2-k,v); px(x+w-r+k,y+h-2-k,v)
rrect(bx,by,bw,bh,3); rrect(bx+2,by+2,bw-4,bh-4,2)                        # case + board edge
for (x,y) in [(bx+5,by+5),(bx+bw-6,by+5),(bx+5,by+bh-6),(bx+bw-6,by+bh-6)]: circ(x,y,1)   # screws
rrect(bx+8,by+3,8,5,1); rect(bx+10,by+5,4,1)                             # usb-c left
rrect(bx+bw-16,by+3,8,5,1); rect(bx+bw-14,by+5,4,1)                      # usb-c right
rrect(bx+22,by+4,28,15,2)                                                 # screen bezel
LOGO=["      ##   ##      ",            # POOM logo: chunky letters, a bar over each O
       "                    ",
       "#### #### #### ##.##",
       "## # ## # ## # #####",
       "#### ## # ## # # # #",
       "##   ## # ## # #   #",
       "##   #### #### #   #"]
for j,row in enumerate(LOGO):
    for i,c in enumerate(row):
        if c=='#': px(bx+26+i,by+8+j,1)
circ(bx+25,by+20,1); circ(bx+46,by+20,1)                                  # screen screws
rect(bx+29,by+24,13,12)                                                   # main module
for (x,y) in [(bx+31,by+26),(bx+31,by+28),(bx+34,by+26)]: px(x,y); px(x+1,y)
rect(bx+31,by+31,9,1); rect(bx+31,by+33,7,1)
rect(bx+bw-15,by+11,10,9); rect(bx+bw-13,by+13,6,1); px(bx+bw-6,by+15,0)   # sd card slot (clear of the button)
rect(bx+10,by+11,5,5,fill=True); px(bx+10,by+11,0)                       # small chip with pins
for k in range(0,5,2): px(bx+9,by+11+k); px(bx+15,by+11+k)
rect(bx+3,by+16,3,6)                                                      # side switch
# d-pad in a clear ring
dx,dy=bx+14,by+34
circ(dx,dy,10)
for (ox,oy) in [(0,-5),(0,5),(-5,0),(5,0)]:
    rect(dx+ox-3,dy+oy-3,7,7,fill=True)
    for (cx_,cy_) in [(-3,-3),(3,-3),(-3,3),(3,3)]: px(dx+ox+cx_,dy+oy+cy_,0)
for k in range(-8,9): px(dx+k,dy+k,0); px(dx+k,dy-k,0)     # gaps between the pads
rect(dx-1,dy-1,3,3,v=0,fill=True); px(dx,dy,1)
# buttons: outer = upper right, inner = lower left, in a slanted pill
ox_,oy_=bx+bw-13,by+30; ix,iy=bx+bw-21,by+38
for t in [i/40 for i in range(41)]:
    import math
    cx=ix+(ox_-ix)*t; cy=iy+(oy_-iy)*t
    for a in range(0,360,6):
        x=cx+7*math.cos(math.radians(a)); y=cy+7*math.sin(math.radians(a))
        d=min(((x-ix)**2+(y-iy)**2)**0.5,((x-ox_)**2+(y-oy_)**2)**0.5)
        # keep only the outer hull of the capsule
        nx,ny=-(oy_-iy),(ox_-ix); L=(nx*nx+ny*ny)**0.5; nx/=L; ny/=L
        dist=abs((x-ix)*nx+(y-iy)*ny); along=((x-ix)*(ox_-ix)+(y-iy)*(oy_-iy))/((ox_-ix)**2+(oy_-iy)**2)
        inside = (dist<6.5 and 0<=along<=1) or ((x-ix)**2+(y-iy)**2)**0.5<6.5 or ((x-ox_)**2+(y-oy_)**2)**0.5<6.5
        if not inside: px(round(x),round(y))
circ(ox_,oy_,4,fill=True); circ(ix,iy,4,fill=True)
# labels + leader lines (each line runs straight from the control to the middle of its word)
tiny((W-8*4)//2,1,"CONTROLS")
TINY['-']=[4,4]
tiny(1,dy-2,"TILT/"); tiny(1,dy+5,"STEER")
for x in range(21,dx-8): px(x,dy)
tiny(104,oy_-2,"PROPEL")
for x in range(ox_+5,103): px(x,oy_)
tiny(108,iy-2,"SPIN"); tiny(110,iy+5,"90")
for (dx,dy) in ((0,0),(1,0),(2,0),(0,1),(2,1),(0,2),(1,2),(2,2)): px(118+dx,iy+5+dy)   # degree sign
for x in range(ix+5,107): px(x,iy)
tiny(32,59,"PRESS ANY BUTTON")
Image.fromarray(S*255).save('controls.png')
Image.fromarray(S*255).resize((512,256),0).save('controls_4x.png')
np.save('controls.npy',S)
