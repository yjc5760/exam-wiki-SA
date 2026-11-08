# SA-2003-1 moment distribution (path 1) + direct stiffness (path 2); clockwise-positive member-end moments, k-ft
import numpy as np
L=30.0; EI=1.0
FEM={'ab':-8*L/8,'ba':8*L/8,'bc':-(1*L**2/12+2*3*L/9),'cb':(1*L**2/12+2*3*L/9),'cd':-8*L/8,'dc':8*L/8}
print("FEM",FEM)
# Path 1: Hardy Cross, full stiffness 4EI/L every member, a,d fixed
M=dict(FEM); DF={'ba':.5,'bc':.5,'cb':.5,'cd':.5}
far={'ba':'ab','bc':'cb','cb':'bc','cd':'dc'}
for it in range(60):
    for j,(m1,m2) in {'b':('ba','bc'),'c':('cb','cd')}.items():
        unb=M[m1]+M[m2]
        for m in (m1,m2):
            d=-DF[m]*unb; M[m]+=d; M[far[m]]+=0.5*d
print("Path1 MD:",{k:round(v,3) for k,v in M.items()})
# Path 2: direct stiffness, unknowns theta_b, theta_c
k=2*EI/L
K=np.array([[2*k+2*k, k],[k, 2*k+2*k]])
P=-np.array([FEM['ba']+FEM['bc'],FEM['cb']+FEM['cd']])
tb,tc=np.linalg.solve(K,P)
M2={'ab':k*tb+FEM['ab'],'ba':2*k*tb+FEM['ba'],'bc':k*(2*tb+tc)+FEM['bc'],
    'cb':k*(2*tc+tb)+FEM['cb'],'cd':2*k*tc+FEM['cd'],'dc':k*tc+FEM['dc']}
print("Path2 SD:",{kk:round(v,3) for kk,v in M2.items()}, "EI*theta_b=",tb*EI,"EI*theta_c=",tc*EI)
# span moments (sagging +)
Mab_mid=8*L/4-(abs(M2['ab'])+abs(M2['ba']))/2
Mbc_mid=1*L**2/8+3*10-abs(M2['bc'])
print("mid ab sag",Mab_mid,"mid bc sag",Mbc_mid)
# reactions
Va=(8*15 + M2['ab']+M2['ba'])/L  # sum moments about b: Va*L - 8*15 - (Mab+Mba)=0 with cw+ end moments
Va=(8*15 - (M2['ab']+M2['ba']))/L
Vb_left=8-Va
Vbc=(1*L*L/2+3*20+3*10 - (M2['bc']+M2['cb']))/L
print("Va",Va,"Vb from ab",Vb_left,"Vb from bc",Vbc,"Rb",Vb_left+Vbc)
# sagging moment functions & inflection points
from scipy.optimize import brentq
Mab=lambda x: M2['ab']+Va*x-8*max(x-15,0)   # M_sag(0) = M_ab (cw on left end = -hog) -> M_sag(0)=M_ab
Mbc=lambda x: M2['bc']+Vbc*x-x*x/2-3*max(x-10,0)-3*max(x-20,0)
print("check Mab(30)=",Mab(30)," (should = -M_ba)", "Mbc(30)=",Mbc(30))
print("ab inflection x from a:",brentq(Mab,0,15),brentq(Mab,15,30))
x1=brentq(Mbc,0,15); print("bc inflection x from b:",x1, 30-x1, "Mbc(10)",Mbc(10),"Mbc(15)",Mbc(15))
