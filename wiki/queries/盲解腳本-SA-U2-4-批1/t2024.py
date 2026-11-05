"""SA-2024-4 側推 P-Δ：事件到事件（event-to-event），塑鉸處另給桿端轉角自由度、增量彎矩為 0"""
import numpy as np
from fr import *
EI=425000.; L=7.; Mpb=300.; Mpc=580.
# 斷面：(桿, 端) -> Mp
secs={('AB',1):('A',Mpc),('AB',2):('B柱頂',Mpc),('BC',1):('B梁端',Mpb),('BC',2):('C梁端',Mpb),('DC',2):('C柱頂',Mpc),('DC',1):('D',Mpc)}
hinges=set(); Mtot={k:0. for k in secs}; Ptot=0.; Dtot=0.; pts=[(0,0)]
for step in range(10):
    u,tB,tC=sp.symbols('u tB tC'); red=[u,tB,tC]; ht={}
    for h in hinges: ht[h]=sp.Symbol('h_%s%d'%h); red.append(ht[h])
    f=Frame(red); f.node('A',0,0); f.node('B',0,2*L,u=u,t=tB); f.node('C',L,2*L,u=u,t=tC); f.node('D',L,0)
    for nm,(n1,n2,E) in {'AB':('A','B',2*EI),'BC':('B','C',EI),'DC':('D','C',2*EI)}.items():
        f.member(n1,n2,E,t1=ht.get((nm,1)),t2=ht.get((nm,2)))
    try:
        K,R,s=f.solve(P=1*u)
    except Exception as e:
        print('機構形成（勁度奇異）'); break
    if any(not sp.Float(v).is_finite for v in s.values()): print('機構'); break
    F=f.end_forces(); dM={}
    for (n1,n2,ff),nm in zip(F,['AB','BC','DC']):
        dM[(nm,1)]=float(ff[2]); dM[(nm,2)]=float(ff[5])
    du=float(s[u])
    # 下一個塑鉸：|M+λdM| = Mp
    lam=1e18; nxt=[]
    for k,(lab,Mp) in secs.items():
        if k in hinges or abs(dM[k])<1e-12: continue
        l=(np.sign(dM[k])*Mp-Mtot[k])/dM[k]
        if l<lam-1e-9: lam=l; nxt=[k]
        elif abs(l-lam)<1e-9: nxt.append(k)
    for k in Mtot: Mtot[k]+=lam*dM[k]
    Ptot+=lam; Dtot+=lam*du; hinges|=set(nxt); pts.append((Dtot,Ptot))
    print(f'事件{step+1}: 切線側向勁度 K_t={1/du:.2f} kN/m, ΔP={lam:.3f}, P={Ptot:.3f} kN, Δ={Dtot*1000:.3f} mm, 新塑鉸={[secs[k][0] for k in nxt]}')
    print('   彎矩(桿端逆時針為正):',{secs[k][0]:round(v,1) for k,v in Mtot.items()})
print('P-Δ 折線點 (mm, kN):',[(round(d*1000,3),round(p,3)) for d,p in pts])
print('機構法檢核: P_u=(2*580+2*300)/(2L)=',(2*580+2*300)/(2*L))
