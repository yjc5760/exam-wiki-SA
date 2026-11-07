import numpy as np
from fem import Model
def beam(xs_key, segs, supports, hinges=(), dx=0.25):
    """xs_key: 關鍵點 dict name->x；segs: [(x0,x1,EI)]；supports: {name:(u,v,th)}；hinges: 內鉸點名稱
    回傳 model 與網格 x 陣列 與節點名列表"""
    keys=sorted(xs_key.values()); L0,L1=keys[0],keys[-1]
    grid=sorted(set(np.round(np.concatenate([np.arange(L0,L1+1e-9,dx),keys]),6)))
    m=Model(); names=[]
    inv={round(v,6):k for k,v in xs_key.items()}
    for i,x in enumerate(grid):
        nm=inv.get(round(x,6),f"n{i}")
        m.node(nm,x,0); names.append(nm)
        if nm in hinges: m.node(nm+"'",x,0,share=nm)
    def EIat(x):
        for a,b,EI in segs:
            if a-1e-9<=x<=b+1e-9: return EI
    for i in range(len(grid)-1):
        a=names[i]; b=names[i+1]
        a2=a+"'" if a in hinges else a
        m.frame(a2,b,EIat((grid[i]+grid[i+1])/2))
    m.support(names[0],u=1)  # 軸向固定一點即可
    for n,(u,v,th) in supports.items(): m.support(n,u,v,th)
    return m,np.array(grid),names
def il(m,names,grid,func):
    out=[]
    for n in names:
        U,R,f=m.solve([(n,0,-1,0)]); out.append(func(U,R,n))
    return np.array(out)
