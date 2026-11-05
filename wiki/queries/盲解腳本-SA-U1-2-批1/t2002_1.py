import numpy as np
Ax,Ay,Hx,Hy=-10,-5/3,4,29/3
# point loads: (x,y,Fx,Fy); couples: (x,y,M ccw) ; distributed moment on CD: -2 per m (cw) from x 0..2 at y=4; dist force GH: Fx=-2/m at x=6, y 0..2
def M_about(P, items):
    px,py=P; return sum((x-px)*fy-(y-py)*fx for x,y,fx,fy in items)
# left column, free body below section at (0,y)
def col_left(y):
    items=[(0,0,Ax,Ay)]; cpl=6 if y>2 else 0
    Mext=M_about((0,y),items)+cpl
    F=np.array([Ax,Ay],float)
    return -F[1], F[0], -Mext  # N(tension+), V(+ = ext force in +x for local n?), M(+ = tension inside/right)
def beam(x):
    # free body: left column + A + loads with x'<x on beam (incl C 10kN)
    items=[(0,0,Ax,Ay),(0,4,10,0)]; cpl=6 - 2*min(x,2)
    if x>3: items.append((3,4,0,-8))
    if x>=6: cpl+=4
    Mext=M_about((x,4),items)+cpl
    F=np.sum([[i[2],i[3]] for i in items],axis=0)
    return -F[0], F[1], -Mext   # N tension+, V (beam conv: left ext force up +), M sagging+
def col_right(y):
    items=[(6,0,Hx,Hy)]
    yy=min(y,2); items.append((6,yy/2,-2*yy,0))
    Mext=M_about((6,y),items)
    F=np.sum([[i[2],i[3]] for i in items],axis=0)
    return -F[1], F[0], -Mext
print('left col y: N V M(+=tension right/inside)')
for y in [0,1,2-1e-9,2+1e-9,3,4]: print(y, np.round(col_left(y),4))
print('beam x: N V M(sag+)')
for x in [0,1,2,3-1e-9,3+1e-9,4,5,6-1e-9]: print(x, np.round(beam(x),4))
print('right col y: N V M(+=tension right/outside)')
for y in [0,1,2,3,4]: print(y, np.round(col_right(y),4))
# column-right top moment just below hinge should be +? couple 4 cw applied at column top -> M at top
# check right col M_ext at F includes couple -4 applied at top: M(4-) vs hinge
