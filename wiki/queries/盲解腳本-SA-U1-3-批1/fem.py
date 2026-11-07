"""平面剛架／桁架勘度法（盲解用）。節點 dof 可共用以模擬內鉸。"""
import numpy as np
class Model:
    def __init__(s): s.nd=0; s.nodes={}; s.els=[]; s.fix=set(); s.springs=[]
    def node(s,name,x,y,share=None):
        """share=另一節點名：共用 u,v，轉角獨立（內鉸）"""
        if share: u,v=s.nodes[share][2][:2]; th=s.nd; s.nd+=1
        else: u,v,th=s.nd,s.nd+1,s.nd+2; s.nd+=3
        s.nodes[name]=(x,y,[u,v,th]); return name
    def frame(s,a,b,EI,EA=1e10): s.els.append(('f',a,b,EI,EA))
    def truss(s,a,b,EA=1.0): s.els.append(('t',a,b,0,EA))
    def support(s,n,u=0,v=0,th=0):
        d=s.nodes[n][2]
        for k,f in zip(d,(u,v,th)):
            if f: s.fix.add(k)
    def geom(s,a,b):
        xa,ya,_=s.nodes[a]; xb,yb,_=s.nodes[b]; L=np.hypot(xb-xa,yb-ya); return L,(xb-xa)/L,(yb-ya)/L
    def kel(s,e):
        t,a,b,EI,EA=e; L,c,sn=s.geom(a,b)
        if t=='t':
            k=EA/L*np.array([[1,0,-1,0],[0,0,0,0],[-1,0,1,0],[0,0,0,0]],float)
            T=np.array([[c,sn,0,0],[-sn,c,0,0],[0,0,c,sn],[0,0,-sn,c]])
            dof=s.nodes[a][2][:2]+s.nodes[b][2][:2]
        else:
            k=np.zeros((6,6)); k[0,0]=k[3,3]=EA/L; k[0,3]=k[3,0]=-EA/L
            m=EI/L**3*np.array([[12,6*L,-12,6*L],[6*L,4*L*L,-6*L,2*L*L],[-12,-6*L,12,-6*L],[6*L,2*L*L,-6*L,4*L*L]])
            idx=[1,2,4,5]
            for i in range(4):
                for j in range(4): k[idx[i],idx[j]]=m[i,j]
            R=np.array([[c,sn,0],[-sn,c,0],[0,0,1]]); T=np.zeros((6,6)); T[:3,:3]=R; T[3:,3:]=R
            dof=s.nodes[a][2]+s.nodes[b][2]
        return k,T,dof
    def solve(s,loads):
        """loads: list of (node, Fx, Fy, M)。回傳 (位移, 反力dict, 桿件軸力list)"""
        K=np.zeros((s.nd,s.nd)); F=np.zeros(s.nd)
        for e in s.els:
            k,T,dof=s.kel(e); kg=T.T@k@T
            for i,di in enumerate(dof):
                for j,dj in enumerate(dof): K[di,dj]+=kg[i,j]
        for n,fx,fy,m in loads:
            d=s.nodes[n][2]; F[d[0]]+=fx; F[d[1]]+=fy; F[d[2]]+=m
        # 沒有任何剛架桿件接到的轉角 dof 一律束制
        used=set()
        for e in s.els:
            if e[0]=='f': used.add(s.nodes[e[1]][2][2]); used.add(s.nodes[e[2]][2][2])
        fixed=set(s.fix)|{s.nodes[n][2][2] for n in s.nodes if s.nodes[n][2][2] not in used}
        free=[i for i in range(s.nd) if i not in fixed]
        U=np.zeros(s.nd); U[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
        Rv=K@U-F
        forces=[]
        for e in s.els:
            k,T,dof=s.kel(e); fl=k@(T@U[dof])
            forces.append(-fl[0] if e[0]=='t' else fl)   # 桁架：拉為正
        return U,Rv,forces
    def dof(s,n,i): return s.nodes[n][2][i]
