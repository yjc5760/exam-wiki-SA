import sys; sys.path.insert(0,'.')
import numpy as np
from fem import solve
for ang in [55,58,60,61,62,65]:
    t=np.radians(ang); A=(-10*np.cos(t),-10*np.sin(t))
    U,out,R=solve({'A':A,'B':(0,0),'C':(12,0),'D':(12,-20)},
       [dict(n1='A',n2='B',EI=1,EA=1e9),dict(n1='B',n2='C',EI=1,EA=1e9,w=2),dict(n1='C',n2='D',EI=1,EA=1e9)],
       {'A':(1,1,1),'D':(1,1,1)},{})
    # 端彎矩（作用於桿件，順時針為正）= -f[2], -f[5]
    em={nm:(-f[2],-f[5]) for nm,f,L in out}
    print(f'AB 與水平夾角 {ang}°: M_AB={em["AB"][0]:+.2f} M_BA={em["AB"][1]:+.2f} M_BC={em["BC"][0]:+.2f} M_CB={em["BC"][1]:+.2f} M_CD={em["CD"][0]:+.2f} M_DC={em["CD"][1]:+.2f}  C: u={U["C"][0]:+.2f} v={U["C"][1]:+.4f} θ={U["C"][2]:+.2f} (×1/EI, θ逆時針+)')
