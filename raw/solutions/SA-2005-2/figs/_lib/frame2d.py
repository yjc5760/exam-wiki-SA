"""2D frame direct stiffness (axial rigid by EA=1e8*EI). End moments reported clockwise-positive on member end (slope-deflection convention)."""
import numpy as np
class Frame:
    def __init__(s): s.N={};s.M=[];s.fix={};s.P={}
    def node(s,n,x,y): s.N[n]=(x,y); s.P[n]=np.zeros(3)
    def support(s,n,ux=0,uy=0,rz=0): s.fix[n]=(ux,uy,rz)  # 1=restrained
    def member(s,name,i,j,EI,w=0.0,rel=(0,0),EA=None):
        s.M.append(dict(name=name,i=i,j=j,EI=EI,w=w,rel=rel,EA=EA or 1e8*EI))
    def load(s,n,fx=0,fy=0,mz=0): s.P[n]+=np.array([fx,fy,mz],float)  # mz CCW+
    def _k(s,m):
        (xi,yi),(xj,yj)=s.N[m['i']],s.N[m['j']];L=np.hypot(xj-xi,yj-yi);c,sn=(xj-xi)/L,(yj-yi)/L
        EI,EA=m['EI'],m['EA']
        k=np.zeros((6,6));k[0,0]=k[3,3]=EA/L;k[0,3]=k[3,0]=-EA/L
        kb=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
        idx=[1,2,4,5]
        for a in range(4):
            for b in range(4): k[idx[a],idx[b]]=kb[a,b]
        # w: transverse load per length in local -y direction (for i->j left to right horizontal, gravity)
        w=m['w'];f=np.array([0,w*L/2,w*L*L/12,0,w*L/2,-w*L*L/12])  # fixed-end reactions (local)
        # releases by static condensation
        for r,pos in ((m['rel'][0],2),(m['rel'][1],5)):
            if r:
                kk=k[:,pos].copy();kp=k[pos,pos]
                f=f-kk*f[pos]/kp;k=k-np.outer(kk,kk)/kp
        T=np.zeros((6,6));R=np.array([[c,sn,0],[-sn,c,0],[0,0,1]]);T[:3,:3]=R;T[3:,3:]=R
        return k,f,T,L
    def solve(s):
        names=list(s.N);dof={n:3*a for a,n in enumerate(names)};n=3*len(names)
        K=np.zeros((n,n));F=np.zeros(n)
        for nm in names: F[dof[nm]:dof[nm]+3]+=s.P[nm]
        for m in s.M:
            k,f,T,L=s._k(m);kg=T.T@k@T;fg=T.T@f
            ids=list(range(dof[m['i']],dof[m['i']]+3))+list(range(dof[m['j']],dof[m['j']]+3))
            K[np.ix_(ids,ids)]+=kg;F[ids]-=fg
        fixed=[dof[nm]+a for nm,r in s.fix.items() for a in range(3) if r[a]]
        free=[a for a in range(n) if a not in fixed]
        # rotational dof of node only attached to released ends -> singular; add tiny
        Kf=K[np.ix_(free,free)]+np.eye(len(free))*1e-12
        d=np.zeros(n);d[free]=np.linalg.solve(Kf,F[free])
        s.d={nm:d[dof[nm]:dof[nm]+3] for nm in names}
        R=K@d-F;s.R={nm:R[dof[nm]:dof[nm]+3] for nm in s.fix}
        s.end={}
        for m in s.M:
            k,f,T,L=s._k(m);ids=list(range(dof[m['i']],dof[m['i']]+3))+list(range(dof[m['j']],dof[m['j']]+3))
            q=k@(T@d[ids])+f;s.end[m['name']]=q  # local: N_i,V_i,M_i(ccw),N_j,V_j,M_j
        return s
    def report(s,unit=''):
        for m in s.M:
            q=s.end[m['name']];print(f"{m['name']}: M_{m['i']}{m['j']}={-q[2]:+.4f}  M_{m['j']}{m['i']}={-q[5]:+.4f}  (CW+)  V_i={q[1]:+.4f} N_i={q[0]:+.4f}")
        for nm,r in s.R.items(): print(f"R_{nm}: Rx={r[0]:+.4f} Ry={r[1]:+.4f} Mz(ccw)={r[2]:+.4f}")
