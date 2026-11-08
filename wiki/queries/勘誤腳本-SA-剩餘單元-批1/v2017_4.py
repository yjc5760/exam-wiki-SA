# SA-2017-4 schematic check: rigid diaphragm torsional stiffness about CR (in-plane wall stiffness ∝ length, unit thickness)
# plan 30 (x) x 12 (y), CM at (15,6). walls: (orient, coord_perp, length)
import numpy as np
L,B=30.,12.
cfg={
 "a":[("y",0,12),("x",0,10),("x",12,10),("y",10,2),("y",10,2)],
 "b":[("x",6,12),("y",15,8)],
 "c":[("x",0,4),("x",0,4),("x",12,4),("x",12,4),("y",0,4),("y",30,4),("y",0,4),("y",30,4),
      ("x",4.5,6),("x",7.5,6),("y",12,1.5),("y",18,1.5),("y",12,1.5),("y",18,1.5)],
}
res={}
for k,w in cfg.items():
    kx=[(c,l) for o,c,l in w if o=="x"]; ky=[(c,l) for o,c,l in w if o=="y"]
    ycr=sum(c*l for c,l in kx)/sum(l for c,l in kx); xcr=sum(c*l for c,l in ky)/sum(l for c,l in ky)
    Kt=sum(l*(c-ycr)**2 for c,l in kx)+sum(l*(c-xcr)**2 for c,l in ky)
    res[k]=(xcr,ycr,abs(xcr-15),Kt); print(k,"CR=(%.2f,%.2f) e_x=%.2f Ktheta=%.1f"%res[k])
mm=0
if not res["b"][3]==0: mm+=1
if not (res["c"][3]>res["a"][3]>res["b"][3]): mm+=1
if not (res["a"][2]>10 and res["b"][2]==0 and res["c"][2]==0): mm+=1
print("MISMATCHES:",mm)
